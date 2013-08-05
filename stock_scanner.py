# -*- coding: utf-8 -*-
##############################################################################
#
#    stock_scanner module for OpenERP, Allows managing barcode readers with simple scenarios
#    Copyright (C) 2011 SYLEAM Info Services (<http://www.syleam.fr/>)
#              Sylvain Garancher <sylvain.garancher@syleam.fr>
#
#    This file is a part of stock_scanner
#
#    stock_scanner is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    stock_scanner is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from osv import orm
from osv import osv
from osv import fields
from tools.translate import _
from tools.misc import ustr
from tools.misc import logged
from threading import Semaphore
import logging
import uuid
import netsvc
import traceback
import sys
from psycopg2 import OperationalError, errorcodes
import random
import time

logger = logging.getLogger('stock_scanner')

_CURSES_COLORS = [
    ('black', _('Black')),
    ('blue', _('Blue')),
    ('cyan', _('Cyan')),
    ('green', _('Green')),
    ('magenta', _('Magenta')),
    ('red', _('Red')),
    ('white', _('White')),
    ('yellow', _('Yellow')),
]

PG_CONCURRENCY_ERRORS_TO_RETRY = (errorcodes.LOCK_NOT_AVAILABLE, errorcodes.SERIALIZATION_FAILURE, errorcodes.DEADLOCK_DETECTED)
MAX_TRIES_ON_CONCURRENCY_FAILURE = 5


class scanner_scenario(osv.osv):
    _name = 'scanner.scenario'
    _description = 'Scenario for scanner'

    _columns = {
        'name': fields.char('Name', size=64, required=True, help='Appear on barcode reader screen'),
        'sequence': fields.integer('Sequence', help='Sequence order'),
        'active': fields.boolean('Active', help='If check, this object is always available'),
        'model_id': fields.many2one('ir.model', 'Model', help='Model used for this scenario'),
        'step_ids': fields.one2many('scanner.scenario.step', 'scenario_id', 'Scenario', ondelete='cascade', help='Step of the current running scenario'),
        'warehouse_ids': fields.many2many('stock.warehouse', 'scanner_scenario_warehouse_rel', 'scenario_id', 'warehouse_id', 'Warehouses', help='Warehouses for this scenario'),
        'notes': fields.text('Notes', help='Store different notes, date and title for modification, etc...'),
        'reference_res_id': fields.char('Rerefence ID', size=64, readonly=True, help='Used by export/import scenario'),
        'shared_custom': fields.boolean('Shared Custom', help='Allows to share the custom values with a shared scanner in the same warehouse'),
        'parent_id': fields.many2one('scanner.scenario', 'Parent', help='Parent scenario, used to create menus'),
        'type': fields.selection([('scenario', 'Scenario'), ('menu', 'Menu'), ('shortcut', 'Shortcut')], 'Type', required=True, help='Defines if this scenario is a menu or an executable scenario'),
    }

    _order = 'sequence'

    _defaults = {
        'type': 'scenario',
    }

    _sql_constraints = [
        ('reference_res_id_uniq', 'unique (reference_res_id)', _('The reference ID of the scenario must be unique !')),
    ]

    _constraints = [
        (lambda self, cr, uid, ids, context=None: self._check_recursion(cr, uid, ids, context=context), _('Error ! You can not create recursive scenarios.'), ['parent_id'])
    ]

    # Dict to save the semaphores
    # Format : {scenario: {warehouse: {reference_document: instance of semaphore}}}
    _semaphores = {}

    def create(self, cr, uid, values, context=None):
        """
        If the reference ID is not in values, we create it with uuid1
        """
        # Generate a uuid if there is none
        if not 'reference_res_id' in values:
            values['reference_res_id'] = uuid.uuid1()

        id = super(scanner_scenario, self).create(cr, uid, values, context=context)
        return id

    def copy_data(self, cr, uid, id, data, context=None):
        data['reference_res_id'] = uuid.uuid1()
        return super(scanner_scenario, self).copy_data(cr, uid, id, data, context=context)

    def _semaphore_acquire(self, cr, uid, id, warehouse_id, reference_document, context=None):
        """
        Make an acquire on a semaphore to take a token
        The semaphore is use like a mutex one on one
        """
        # Retrieve the active semaphore
        semaphore = self._semaphores.get(id, {}).get(warehouse_id, {}).get(reference_document, None)

        # If there is no semaphore, create a new one
        if semaphore is None:
            semaphore = Semaphore()

            # No semaphore for this scenario
            if not self._semaphores.get(id, False):
                self._semaphores[id] = {}

            # no semaphore for this scenario in this warehouse
            if not self._semaphores[id].get(warehouse_id, False):
                self._semaphores[id][warehouse_id] = {}

            # Store the semaphore
            self._semaphores[id][warehouse_id][reference_document] = semaphore

        # Acquire the mutex
        semaphore.acquire()

    def _semaphore_release(self, cr, uid, id, warehouse_id, reference_document, context=None):
        """
        Make a release on a semaphore to free a token
        The semaphore is use like a mutex one on one
        """
        self._semaphores[id][warehouse_id][reference_document].release()

scanner_scenario()


class scanner_scenario_step(osv.osv):
    _name = 'scanner.scenario.step'
    _description = 'Step for scenario'

    _columns = {
        'name': fields.char('Name', size=64, help='Name of the step'),
        'scenario_id': fields.many2one('scanner.scenario', 'Scenario', ondelete='cascade', required=True, help='Scenario for this step'),
        'step_start': fields.boolean('Step start', help='Check this if this is the first step of the scenario'),
        'step_stop': fields.boolean('Step stop', help='Check this if this is the  last step of the scenario'),
        'step_back': fields.boolean('Step back', help='Check this to stop at this step when returning back'),
        'out_transition_ids': fields.one2many('scanner.scenario.transition', 'from_id', 'Outgoing transitons', ondelete='cascade', help='Transitions which goes to this step'),
        'in_transition_ids': fields.one2many('scanner.scenario.transition', 'to_id', 'Incoming transitions', ondelete='cascade', help='Transitions which goes to the next step'),
        'python_code': fields.text('Python code', help='Python code to execute'),
        'reference_res_id': fields.char('Reference ID', size=64, readonly=True, help='Used by export/import scenario/step'),
    }

    _defaults = {
        'step_start': False,
        'step_stop': False,
        'python_code': '# Use <m> or <message> to retrieve the data transmitted by the scanner.\n'
                       '# Use <t> or <terminal> to retrieve the running terminal browse record.\n'
                       '# Put the returned action code in <act>, as a single character.\n'
                       '# Put the returned result or message in <res>, as a list of strings.\n'
                       '# Put the returned value in <val>, as an integer',
    }

    _sql_constraints = [
        ('reference_res_id_uniq', 'unique (reference_res_id)', _('The reference ID of the step must be unique')),
    ]

    def create(self, cr, uid, values, context=None):
        """
        If the reference ID is not in values, we create it with uuid1
        """
        if not 'reference_res_id' in values:
            values['reference_res_id'] = uuid.uuid1()

        id = super(scanner_scenario_step, self).create(cr, uid, values, context=context)
        return id

    def copy_data(self, cr, uid, id, data, context=None):
        data['reference_res_id'] = uuid.uuid1()
        return super(scanner_scenario_step, self).copy_data(cr, uid, id, data, context=context)

scanner_scenario_step()


class scanner_scenario_transition(osv.osv):
    _name = 'scanner.scenario.transition'
    _description = 'Transition for senario'

    _columns = {
        'name': fields.char('Name', size=64, required=True, help='Name of the transition'),
        'sequence': fields.integer('Sequence', help='Sequence order'),
        'from_id': fields.many2one('scanner.scenario.step', 'From', required=True, ondelete='cascade', help='Step which launches this transition'),
        'to_id': fields.many2one('scanner.scenario.step', 'To', required=True, ondelete='cascade', help='Step which is reached by this transition'),
        'condition': fields.char('Condition', size=256, required=True, help='The transition is followed only if this condition is evaluated as True'),
        'transition_type': fields.selection([('scanner', 'Scanner'), ('keyboard', 'Keyboard')], 'Transition Type', help='Type of transition'),
        'tracer': fields.char('Tracer', size=12, help='Used to determine fron which transition we arrive to the destination step'),
        'reference_res_id': fields.char('Reference ID', size=64, readonly=True, help='Used by export/import scenario/transition'),
        'scenario_id': fields.related('from_id', 'scenario_id', type="many2one", relation="scanner.scenario", string="Scenario", store=True),
    }

    _order = 'sequence'

    _defaults = {
        'condition': 'True',
        'transition_type': 'scanner',
        'tracer': False,
    }

    def _check_scenario(self, cr, uid, ids, context=None):
        """
        Check if the steps and the transition are on the same scenario
        """
        for transition in self.browse(cr, uid, ids, context=context):
            if transition.from_id.scenario_id.id != transition.to_id.scenario_id.id:
                return False

        return True

    _constraints = [
        (_check_scenario, _('Error : The transition must link steps of the same scenario !'), ['from_id', 'to_id']),
    ]

    _sql_constraints = [
        ('reference_res_id_uniq', 'unique (reference_res_id)', _('The reference ID of the transition must be unique')),
    ]

    def create(self, cr, uid, values, context=None):
        """
        If the reference ID is not in values, we create it with uuid1
        """
        if not 'reference_res_id' in values:
            values['reference_res_id'] = uuid.uuid1()

        id = super(scanner_scenario_transition, self).create(cr, uid, values, context=context)
        return id

    def copy_data(self, cr, uid, id, data, context=None):
        data['reference_res_id'] = uuid.uuid1()
        return super(scanner_scenario_transition, self).copy_data(cr, uid, id, data, context=context)

scanner_scenario_transition()


class scanner_hardware(osv.osv):
    _name = 'scanner.hardware'
    _description = 'Scanner Hardware'

    _columns = {
        'name': fields.char('Name', size=128, required=True, help='Name of the hardware'),
        'code': fields.char('Code', size=128, required=True, help='Code of this hardware'),
        'log_enabled': fields.boolean('Log enabled', help='Enable logging messages from scenarios'),
        'screen_width': fields.integer('Screen Width', help='Width of the terminal\'s screen'),
        'screen_height': fields.integer('Screen Height', help='Height of the terminal\'s screen'),
        'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse', required=True, help='Warehouse where is located this hardware'),
        'user_id': fields.many2one('res.users', 'User', help='Allow to define an other user for execute all scenarios with that scanner instead of default user'),
        'scenario_id': fields.many2one('scanner.scenario', 'Scenario', help='Scenario used for this hardware'),
        'step_id': fields.many2one('scanner.scenario.step', 'Current Step', help='Current step for this hardware'),
        'previous_steps_id': fields.text('Previous Step', help='Previous step for this hardware'),
        'previous_steps_message': fields.text('Previous Message', help='Previous message for this hardware'),
        'reference_document': fields.integer('Reference', help='ID of the reference document'),
        'tmp_val1': fields.char('Temp value 1', size=256, help='Temporary value'),
        'tmp_val2': fields.char('Temp value 2', size=256, help='Temporary value'),
        'tmp_val3': fields.char('Temp value 3', size=256, help='Temporary value'),
        'tmp_val4': fields.char('Temp value 4', size=256, help='Temporary value'),
        'tmp_val5': fields.char('Temp value 5', size=256, help='Temporary value'),
        # Define colors used on the terminal
        'base_fg_color': fields.selection(_CURSES_COLORS, 'Base - Text Color', required=True, help='Default color for the text'),
        'base_bg_color': fields.selection(_CURSES_COLORS, 'Base - Background Color', required=True, help='Default color for the background'),
        'info_fg_color': fields.selection(_CURSES_COLORS, 'Info - Text Color', required=True, help='Color for the info text'),
        'info_bg_color': fields.selection(_CURSES_COLORS, 'Info - Background Color', required=True, help='Color for the info background'),
        'error_fg_color': fields.selection(_CURSES_COLORS, 'Error - Text Color', required=True, help='Color for the error text'),
        'error_bg_color': fields.selection(_CURSES_COLORS, 'Error - Background Color', required=True, help='Color for the error background'),
    }

    _defaults = {
        'screen_width': 20,
        'screen_height': 4,
        'scenario_id': False,
        'step_id': False,
        'reference_document': False,
        'previous_steps_id': '',
        'previous_steps_message': '',
        # Default colors
        'base_fg_color': 'white',
        'base_bg_color': 'blue',
        'info_fg_color': 'yellow',
        'info_bg_color': 'blue',
        'error_fg_color': 'yellow',
        'error_bg_color': 'red',
    }

    def search_scanner_id(self, cr, uid, numterm=False, context=None):
        if context is None:
            context = self.pool.get('res.users').context_get(cr, uid)

        term_id = self.search(cr, uid, [('code', '=', numterm)])
        if not term_id:
            logger.warn('Terminal %s not exists!' % numterm)
            raise osv.except_osv(_('Error'), _('This terminal not exists!'))

        return term_id[0]

    @logged
    def scanner_size(self, cr, uid, terminal_number, context=None):
        """
        Retrieve the size of the screen defined for this scanner

        :return: Return width and height of the screen
        :rtype: tuple
        """
        term_id = self.search_scanner_id(cr, uid, terminal_number, context=context)
        terminal = self.browse(cr, uid, term_id, context=context)
        return (terminal.screen_width, terminal.screen_height)

    @logged
    def scanner_check(self, cr, uid, terminal_number, context=None):
        """
        Check the step for this scanner
        """
        if context is None:
            context = self.pool.get('res.users').context_get(cr, uid, context=context)

        # Retrieve the terminal id from its number
        terminal_ids = self.search(cr, uid, [('code', '=', terminal_number)], context=context)

        # No terminal for the requested number : Error
        if not terminal_ids:
            logger.warning('Terminal %s not found !' % terminal_number)
            raise osv.except_osv(_('Error'), _('Terminal not found !'))

        # Retrieve scenario id from terminal
        terminal_data = self.read(cr, uid, terminal_ids[0], ['scenario_id'], context=context)

        # Return the scenadio id if the terminal has a scenario or False
        return terminal_data.get('scenario_id', False)

    @logged
    def scanner_call(self, cr, uid, terminal_number, action, message=False, transition_type='keyboard', context=None):
        """
        This method is called by the barcode reader,
        """
        if context is None:
            context = self.pool.get('res.users').context_get(cr, uid, context=context)
        # Retrieve the terminal id
        terminal_ids = self.search(cr, uid, [('code', '=', terminal_number)], context=context)
        if not terminal_ids:
            raise osv.except_osv(_('Error'), _('This terminal is not declared !'))

        scanner_scenario_obj = self.pool.get('scanner.scenario')

        # Retrieve the terminal
        terminal = self.browse(cr, uid, terminal_ids[0], context=context)

        # Change uid if defined on the stock scanner
        uid = terminal.user_id and terminal.user_id.id or uid

        # Retrieve the terminal screen size
        if action == 'screen_size':
            logger.debug('Retrieve screen size')
            screen_size = self._screen_size(cr, uid, terminal.id, context=context)
            return ('M', screen_size, 0)

        # Retrieve the terminal screen colors
        if action == 'screen_colors':
            logger.debug('Retrieve screen colors')
            screen_colors = {
                'base': (terminal.base_fg_color, terminal.base_bg_color),
                'info': (terminal.info_fg_color, terminal.info_bg_color),
                'error': (terminal.error_fg_color, terminal.error_bg_color),
            }
            return ('M', screen_colors, 0)

        # Execute the action
        elif action == 'action':
            # The terminal is attached to a scenario
            if terminal.scenario_id:
                return self._scenario_save(cr, uid, terminal.id,
                                           message,
                                           transition_type,
                                           scenario_id=terminal.scenario_id.id,
                                           step_id=terminal.step_id.id,
                                           current_object=terminal.reference_document,
                                           context=context)
            # We asked for a scan transition type, but no action is running, forbidden
            elif transition_type == 'scanner':
                return self._unknown_action(cr, uid, [terminal.id],
                                            ['Forbidden', 'action'],
                                            context=context)
            # No action to do
            else:
                logger.info('[%s] Action : %s (no current scenario)',
                            terminal_number, message)
                scenario_ids = scanner_scenario_obj.search(cr, uid,
                                                           [('name', '=', message),
                                                            ('type', '=', 'menu'),
                                                            ('warehouse_ids', 'in', [terminal.warehouse_id.id])],
                                                           context=context)
                if message == -1:
                    scenario_ids = [False]
                if scenario_ids:
                    scenarios = self._scenario_list(cr, uid,
                                                    terminal.warehouse_id.id,
                                                    parent_id=scenario_ids[0],
                                                    context=context)
                    if scenarios:
                        menu_name = scanner_scenario_obj.browse(cr, uid,
                                                                scenario_ids[0],
                                                                context=context).name
                        return ('L', ['|%s' % menu_name] + scenarios, 0)
                return self._scenario_save(cr, uid, terminal.id,
                                           message,
                                           transition_type,
                                           context=context)

        # Reload current step
        elif action == 'restart':
            # The terminal is attached to a scenario
            if terminal.scenario_id:
                return self._scenario_save(cr, uid,
                                           terminal.id,
                                           message,
                                           'restart',
                                           scenario_id=terminal.scenario_id.id,
                                           current_object=terminal.reference_document,
                                           context=context)

        # Reload previous step
        elif action == 'back':
            # The terminal is attached to a scenario
            if terminal.scenario_id:
                return self._scenario_save(cr, uid,
                                           terminal.id,
                                           message,
                                           'back',
                                           scenario_id=terminal.scenario_id.id,
                                           current_object=terminal.reference_document,
                                           context=context)

        # End required
        elif action == 'end':
            # Empty the values
            logger.info('[%s] End scenario request' % terminal_number)
            self.empty_scanner_values(cr, uid, terminal_ids, context=context)

            return ('F', [_('This scenario'), _('is finished')], '')

        # If the terminal is not attached to a scenario, send the menu (scenario list)
        if not terminal.scenario_id:
            logger.info('[%s] No running scenario' % terminal_number)
            scenarios = self._scenario_list(cr, uid, terminal.warehouse_id.id, message, context=context)
            return ('L', scenarios, 0)

        # Nothing matched, return an error
        return self._send_error(cr, uid, [terminal.id], ['Unknown', 'action'], context=context)

    def _send_error(self, cr, uid, ids, message, context=None):
        """
        Sends an error message
        """
        self.empty_scanner_values(cr, uid, ids, context=context)
        return ('R', message, 0)

    def _unknown_action(self, cr, uid, ids, message, context=None):
        """
        Sends an unknown action message
        """
        return ('U', message, 0)

    def empty_scanner_values(self, cr, uid, ids, context=None):
        """
        This method empty all temporary values, scenario, step and reference_document
        Because if we want reset term when error we must use sql query, it is bad in production
        """
        scenario_custom_obj = self.pool.get('scanner.scenario.custom')

        # Remove values in all scenarios used by "ids" scanners
        for scanner in self.browse(cr, uid, ids, context=context):
            if scanner.scenario_id and scanner.scenario_id.id:
                scenario_custom_obj._remove_values(cr, uid, scanner.scenario_id, scanner, context=context)

        # Write empty values in all fields
        self.write(cr, uid, ids, {
            'scenario_id': False,
            'step_id': False,
            'previous_steps_id': '',
            'previous_steps_message': '',
            'reference_document': 0,
            'tmp_val1': '',
            'tmp_val2': '',
            'tmp_val3': '',
            'tmp_val4': '',
            'tmp_val5': '',
        }, context=context)

        return True

    def scanner_end(self, cr, uid, numterm=None, context=None):
        """
        End the end barcode is read, we execute this step
        """
        if context is None:
            context = self.pool.get('res.users').context_get(cr, uid)

        term_id = self.search_scanner_id(cr, uid, numterm, context=context)
        return self.scanner_call(cr, uid, terminal_number=numterm, action='end')

    def _memorize(self, cr, uid, terminal_id, scenario_id, step_id, previous_steps_id=False, previous_steps_message=False, object=None, context=None):
        """
        After affect a scenario to a scanner, we must memorize it
        If object is specify, save it as well (ex: res.partner,12)
        """
        if context is None:
            context = self.pool.get('res.users').context_get(cr, uid, context=context)

        args = {
            'scenario_id': scenario_id,
            'step_id': step_id,
            'previous_steps_id': previous_steps_id,
            'previous_steps_message': previous_steps_message,
        }
        if object is not None and isinstance(object, int):
            args['reference_document'] = object

        self.write(cr, uid, [terminal_id], args, context=context)

    @logged
    def _scenario_save(self, cr, uid, terminal_id, message, transition_type, scenario_id=None, step_id=None, current_object='', context=None):
        """
        Save the scenario on this terminal and execute the current step
        Return the action to the terminal
        """
        if context is None:
            context = self.pool.get('res.users').context_get(cr, uid, context=context)

        scanner_scenario_obj = self.pool.get('scanner.scenario')
        scanner_step_obj = self.pool.get('scanner.scenario.step')
        terminal = self.browse(cr, uid, terminal_id, context=context)

        tracer = False

        if transition_type == 'restart' or scenario_id and step_id is None:
            if terminal.previous_steps_id:
                # Retrieve previous step id and message
                previous_steps_id = terminal.previous_steps_id.split(',')
                previous_steps_message = terminal.previous_steps_message.split('\n')
                if transition_type != 'restart':
                    previous_steps_id.pop()
                    previous_steps_message.pop()

                if not previous_steps_id:
                    return self.scanner_end(cr, uid, numterm=terminal.code, context=context)

                # Retrieve step id
                step_id = int(previous_steps_id.pop())
                terminal.previous_steps_id = ','.join(previous_steps_id)

                # Retrieve message
                message = eval(previous_steps_message.pop())
                terminal.previous_steps_message = '\n'.join(previous_steps_message)
            else:
                scenario_id = False
                message = terminal.scenario_id.name

        # No scenario in arguments, start a new one
        if not scenario_id:
            # Retrieve the terminal's warehouse
            terminal_warehouse_ids = self.read(cr, uid, terminal_id, ['warehouse_id'], context=context).get('warehouse_id', False)
            # Retrieve the warehouse's scenarios
            scenario_ids = terminal_warehouse_ids and scanner_scenario_obj.search(cr, uid, [('name', '=', message), ('type', '=', 'scenario'), ('warehouse_ids', 'in', [terminal_warehouse_ids[0]])], context=context) or []

            # If at least one scenario was found, pick the start step of the first
            if scenario_ids:
                scenario_id = scenario_ids[0]
                step_ids = scanner_step_obj.search(cr, uid, [('scenario_id', '=', scenario_id), ('step_start', '=', True)], context=context)

                # No start step found on the scenario, return an error
                if not step_ids:
                    return self._send_error(cr, uid, [terminal_id], [_('Please contact'), _('your'), _('administrator'), _('A001')], context=context)

                step_id = step_ids[0]

            else:
                return self._send_error(cr, uid, [terminal_id], [_('Scenario'), _('not found')], context=context)
        elif transition_type != 'none':
            # Retrieve outgoing transitions from the current step
            scanner_transition_obj = self.pool.get('scanner.scenario.transition')
            transition_ids = scanner_transition_obj.search(cr, uid, [('from_id', '=', step_id)], context=context)

            # Evaluate the condition for each transition
            for transition in scanner_transition_obj.browse(cr, uid, transition_ids, context=context):
                step_id = False
                tracer = ''
                ctx = {
                    'context': context,
                    'model': self.pool.get(transition.from_id.scenario_id.model_id.model),
                    'cr': cr,
                    'pool': self.pool,
                    'uid': uid,
                    'm': message,
                    'message': message,
                    't': self.browse(cr, uid, terminal_id, context=context),
                    'terminal': self.browse(cr, uid, terminal_id, context=context),
                }
                expr = eval(str(transition.condition), ctx)

                # Invalid condition, evaluate next transition
                if not expr:
                    continue

                # Condition passed, go to this step
                step_id = transition.to_id.id
                tracer = transition.tracer

                # Store the old step id if we are on a back step
                if transition.to_id.step_back and terminal.previous_steps_id.split(',')[-1] != str(transition.from_id.id):
                    terminal.previous_steps_message = terminal.previous_steps_id and '%s\n%s' % (terminal.previous_steps_message, repr(message)) or repr(message)
                    terminal.previous_steps_id = terminal.previous_steps_id and '%s,%d' % (terminal.previous_steps_id, transition.from_id.id) or str(transition.from_id.id)

                # Valid transition found, stop searching
                break

            # No step found, return an error
            if not step_id:
                terminal.log('No valid transition found !')
                return self._unknown_action(cr, uid, [terminal_id], [_('Please contact'), _('your'), _('adminstrator')], context=context)

        # Memorize the current step
        self._memorize(cr, uid, terminal_id, scenario_id, step_id, previous_steps_id=terminal.previous_steps_id, previous_steps_message=terminal.previous_steps_message, object=current_object, context=context)

        # MUTEX Acquire
        scanner_scenario_obj._semaphore_acquire(cr, uid, terminal.scenario_id.id, terminal.warehouse_id.id, terminal.reference_document, context=context)

        # Execute the step
        step = scanner_step_obj.browse(cr, uid, step_id, context=context)

        ld = {
            'cr': cr,
            'uid': uid,
            'pool': self.pool,
            'model': self.pool.get(step.scenario_id.model_id.model),
            'custom': self.pool.get('scanner.scenario.custom'),
            'term': self,
            'context': context,
            'm': message,
            'message': message,
            't': terminal,
            'terminal': terminal,
            'tracer': tracer,
            'wkf': netsvc.LocalService('workflow'),
            'workflow': netsvc.LocalService('workflow'),
            'scenario': scanner_scenario_obj.browse(cr, uid, scenario_id, context=context),
        }

        tries = 0
        loop_test = True
        while loop_test:
            try:
                terminal.log('Executing step %d : %s' % (step_id, step.name))
                terminal.log('Message : %s' % repr(message))
                if tracer:
                    terminal.log('Tracer : %s' % repr(tracer))

                exec step.python_code in ld
                if step.step_stop:
                    self.empty_scanner_values(cr, uid, [terminal_id], context=context)
                loop_test = False
            except OperationalError, e:
                # Automatically retry the typical transaction serialization errors
                if e.pgcode not in PG_CONCURRENCY_ERRORS_TO_RETRY:
                    ld = {'act': 'R', 'res': ['Please contact', 'your', 'administrator'], 'val': 0}
                    loop_test = False
                if tries >= MAX_TRIES_ON_CONCURRENCY_FAILURE:
                    logger.warning("Concurrent transaction - OperationalError %s, maximum number of tries reached" % e.pgcode)
                    ld = {'act': 'E', 'res': [u'Concurrent transaction - OperationalError %s, maximum number of tries reached' % (e.pgcode)], 'val': True}
                    loop_test = False
                wait_time = random.uniform(0.0, 2 ** tries)
                tries += 1
                logger.info("Concurrent transaction detected (%s), retrying %d/%d in %.04f sec..." % (e.pgcode, tries, MAX_TRIES_ON_CONCURRENCY_FAILURE, wait_time))
                time.sleep(wait_time)
            except orm.except_orm, e:
                # ORM exception, display the error message and require the "go back" action
                cr.rollback()
                ld = {'act': 'E', 'res': [e.name, u'', e.value], 'val': True}
                logger.warning('OSV Exception: %s' % reduce(lambda x, y: x + y, traceback.format_exception(*sys.exc_info())))
                loop_test = False
            except osv.except_osv, e:
                # OSV exception, display the error message and require the "go back" action
                cr.rollback()
                ld = {'act': 'E', 'res': [e.name, u'', e.value], 'val': True}
                logger.warning('OSV Exception: %s' % reduce(lambda x, y: x + y, traceback.format_exception(*sys.exc_info())))
                loop_test = False
            except Exception, e:
                cr.rollback()
                ld = {'act': 'R', 'res': ['Please contact', 'your', 'administrator'], 'val': 0}
                self.empty_scanner_values(cr, uid, [terminal_id], context=context)
                logger.error('Exception: %s' % reduce(lambda x, y: x + y, traceback.format_exception(*sys.exc_info())))
                loop_test = False
            finally:
                scanner_scenario_obj._semaphore_release(cr, uid, terminal.scenario_id.id, terminal.warehouse_id.id, terminal.reference_document, context=context)

        ret = (ld.get('act', 'M'), ld.get('res', ['nothing']), ld.get('val', 0))
        terminal.log('Return value : %s' % repr(ret))

        return ret

    def _scenario_list(self, cr, uid, warehouse_id, parent_id=False, context=None):
        """
        Retrieve the scenario list for this warehouse
        """
        if context is None:
            context = self.pool.get('res.users').context_get(cr, uid, context=context)

        scanner_scenario_obj = self.pool.get('scanner.scenario')
        scanner_scenario_ids = scanner_scenario_obj.search(cr, uid, [('warehouse_ids', 'in', [warehouse_id]), ('parent_id', '=', parent_id)], context=context)
        scanner_scenario_data = scanner_scenario_obj.read(cr, uid, scanner_scenario_ids, ['name'], context=context)

        return_value = [data['name'] for data in scanner_scenario_data if data.get('name', False)]
        return return_value

    def _screen_size(self, cr, uid, terminal_id, context=None):
        """
        Retrieve the screen size for this terminal
        """
        if context is None:
            context = self.pool.get('res.users').context_get(cr, uid, context=context)

        data = self.read(cr, uid, terminal_id, ['screen_width', 'screen_height'], context=context)

        return (data['screen_width'], data['screen_height'])

    def log(self, cr, uid, ids, log_message, context=None):
        """
        Writes a log line if enabled for the terminal
        """
        for terminal in self.browse(cr, uid, ids, context=context):
            if terminal.log_enabled:
                logger.info('[%s] %s' % (terminal.code, ustr(log_message)))

scanner_hardware()


class scanner_scenario_custom(osv.osv):
    _name = 'scanner.scenario.custom'
    _description = 'Temporary value for scenario'

    _columns = {
        # Link data to scenario
        'scenario_id': fields.many2one('scanner.scenario', 'Scenario', ondelete='cascade', help='Values used for this scenario'),
        'scanner_id': fields.many2one('scanner.hardware', 'Scanner', ondelete='cascade', help='Values used for this scanner'),
        'model': fields.char('Model', size=255, required=True, help='Model used for these data'),
        'res_id': fields.integer('Values id', required=True, help='ID of the model source'),
        # Temporary fields
        'char_val1': fields.char('Char Value 1', size=255, help='Temporary char value'),
        'char_val2': fields.char('Char Value 2', size=255, help='Temporary char value'),
        'char_val3': fields.char('Char Value 3', size=255, help='Temporary char value'),
        'char_val4': fields.char('Char Value 4', size=255, help='Temporary char value'),
        'char_val5': fields.char('Char Value 5', size=255, help='Temporary char value'),
        'int_val1': fields.integer('Int Value 1', help='Temporary int value'),
        'int_val2': fields.integer('Int Value 2', help='Temporary int value'),
        'int_val3': fields.integer('Int Value 3', help='Temporary int value'),
        'int_val4': fields.integer('Int Value 4', help='Temporary int value'),
        'int_val5': fields.integer('Int Value 5', help='Temporary int value'),
        'float_val1': fields.float('Float Value 1', help='Temporary float value'),
        'float_val2': fields.float('Float Value 2', help='Temporary float value'),
        'float_val3': fields.float('Float Value 3', help='Temporary float value'),
        'float_val4': fields.float('Float Value 4', help='Temporary float value'),
        'float_val5': fields.float('Float Value 5', help='Temporary float value'),
        'text_val': fields.text('Text', help='Temporary text value'),
    }

    _defaults = {
        'char_val1': '',
        'char_val2': '',
        'char_val3': '',
        'char_val4': '',
        'char_val5': '',
        'int_val1': 0,
        'int_val2': 0,
        'int_val3': 0,
        'int_val4': 0,
        'int_val5': 0,
        'float_val1': 0.,
        'float_val2': 0.,
        'float_val3': 0.,
        'float_val4': 0.,
        'float_val5': 0.,
        'text_val': '',
    }

    def _get_domain(self, cr, uid, scenario, scanner, context=None):
        """
        Create a domain to find custom values.
        Use the fields shared_custom of scenario and scanner
        """
        # Domain if custom values are shared
        if scenario.shared_custom == True:
            return [('scenario_id', '=', scenario.id), ('scanner_id.reference_document', '=', scanner.reference_document), ('scanner_id.warehouse_id', '=', scanner.warehouse_id.id)]

        # Default domain
        return [('scenario_id', '=', scenario.id), ('scanner_id', '=', scanner.id)]

    def _get_values(self, cr, uid, scenario, scanner, model='', res_id=None, domain=None, context=None):
        """
        Returns read customs line
        @param domain : list of tuple for search method
        """
        # Get the default search domain
        search_domain = self._get_domain(cr, uid, scenario, scanner, context=context)

        # Add custom values in search domain
        if domain is not None:
            search_domain.extend(domain)

        # Add model in search domain, if any
        if model:
            search_domain.append(('model', '=', model))

        # Add res_id in search domain, if any
        if res_id:
            search_domain.append(('res_id', '=', res_id))

        # Search for values
        ids = self.search(cr, uid, search_domain, context=context)

        # If ids were found, return data from these ids
        if ids:
            return self.read(cr, uid, ids, [], context=context)

        # No id found, return an empty list
        return []

    def _set_values(self, cr, uid, values, context=None):
        """
        values is a dict, from a 'read' function
        Get id in values and delete some fields
        """
        # Copy values to let original dict unchanged
        vals = values.copy()

        # Get id from values, in a list
        ids = [values.get('id', None)]

        # Remove unwanted fields from vals
        for key in ['id', 'scenario_id', 'scanner_id', 'model', 'res_id']:
            if key in vals:
                del vals[key]

        # Write new values
        return self.write(cr, uid, ids, vals, context=context)

    def _remove_values(self, cr, uid, scenario, scanner, context=None):
        """
        Unlink all the line links from current scenario
        """
        scanner_hardware_obj = self.pool.get('scanner.hardware')
        scanner_ids = []

        # If custom values are shared, search for other hardware using the same
        if scenario.shared_custom == True:
            scanner_ids = scanner_hardware_obj.search(cr, uid, [('scenario_id', '=', scenario.id), ('warehouse_id', '=', scanner.warehouse_id.id), ('reference_document', '=', scanner.reference_document), ('id', '!=', scanner.id)], context=context)

        # Search for values attached to the current scenario
        ids = self.search(cr, uid, [('scenario_id', '=', scenario.id), ('scanner_id', '=', scanner.id)], context=context)

        # If other scanners are on the current scenario, attach the first
        if scanner_ids:
            return self.write(cr, uid, ids, {'scanner_id': scanner_ids[0]}, context=context)

        # Else, delete the current custom values
        return self.unlink(cr, uid, ids, context=context)

scanner_scenario_custom()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
