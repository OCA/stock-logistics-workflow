# -*- coding: utf-8 -*-
##############################################################################
#
#    stock_scanner module for OpenERP, Allows managing barcode readers with
#    simple scenarios
#    Copyright (C) 2011 SYLEAM Info Services (<http://www.syleam.fr/>)
#              Sylvain Garancher <sylvain.garancher@syleam.fr>

#    This file is a part of stock_scanner
#
#    stock_scanner is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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


from openerp import models
from openerp import fields
from openerp import api
from openerp import _
from openerp.tools.misc import logged
from openerp.tools.misc import ustr
from openerp import workflow
from openerp.exceptions import Warning
from openerp.exceptions import except_orm

from threading import Semaphore
import logging
import uuid
from psycopg2 import OperationalError, errorcodes
import random
import time

from .common import PYTHON_CODE_DEFAULT

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

PG_CONCURRENCY_ERRORS_TO_RETRY = (
    errorcodes.LOCK_NOT_AVAILABLE,
    errorcodes.SERIALIZATION_FAILURE,
    errorcodes.DEADLOCK_DETECTED)
MAX_TRIES_ON_CONCURRENCY_FAILURE = 5


class scanner_scenario(models.Model):
    _name = 'scanner.scenario'
    _description = 'Scenario for scanner'

    _order = 'sequence'

    _parent_name = 'parent_id'

    @api.model
    def _type_get(self):
        return [
            ('scenario', 'Scenario'),
            ('menu', 'Menu'),
            ('shortcut', 'Shortcut'),
        ]

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(
        string='Name',
        size=64,
        required=True,
        help='Appear on barcode reader screen')
    sequence = fields.Integer(
        string='Sequence',
        default=0,
        required=False,
        help="Sequence order")
    active = fields.Boolean(
        string='Active',
        default=True,
        help='If check, this object is always available')
    model_id = fields.Many2one(
        'ir.model',
        string='Model',
        required=False,
        ondelete='restrict',
        help='Model used for this scenario')
    step_ids = fields.One2many(
        'scanner.scenario.step',
        'scenario_id',
        string='Scenario',
        ondelete='cascade',
        help='Step of the current running scenario')
    warehouse_ids = fields.Many2many(
        'stock.warehouse',
        'scanner_scenario_warehouse_rel',
        'scenario_id',
        'warehouse_id',
        'Warehouses',
        help='Warehouses for this scenario')
    notes = fields.Text(
        string='Notes',
        help='Store different notes, date and title for modification, etc...')
    reference_res_id = fields.Char(
        string='Reference ID',
        size=64,
        copy=False,
        default=lambda self: uuid.uuid1(),
        required=False,
        readonly=True,
        help='Used by export/import scenario')
    shared_custom = fields.Boolean(
        string='Shared Custom',
        default=False,
        help='Allows to share the custom values with a shared scanner in the '
             'same warehouse')
    parent_id = fields.Many2one(
        'scanner.scenario',
        string='Parent',
        required=False,
        ondelete='restrict',
        help='Parent scenario, used to create menus')
    type = fields.Selection(
        '_type_get',
        string='Type',
        required=True,
        default='scenario',
        help='Defines if this scenario is a menu or an executable scenario')
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.user.company_id.id,
        ondelete='restrict',
        help='Company to be used on this scenario')

    _sql_constraints = [
        ('reference_res_id_uniq',
         'unique (reference_res_id)',
         _('The reference ID of the scenario must be unique !')),
    ]

    @api.one
    @api.constrains('parent_id')
    def _check_recursion(self):
        if not super(scanner_scenario, self)._check_recursion():
            raise Warning(_('Error ! You can not create recursive scenarios.'))

    # Dict to save the semaphores
    # Format : {scenario: {warehouse: {reference_document: instance of
    # semaphore}}}
    _semaphores = {}

    @api.model
    def create(self, vals):
        """
        If the reference ID is not in vals, we create it with uuid1
        """
        # Generate a uuid if there is none
        if 'reference_res_id' not in vals:
            vals['reference_res_id'] = uuid.uuid1()

        return super(scanner_scenario, self).create(vals=vals)

    def _semaphore_acquire(self, warehouse_id, reference_document):
        """
        Make an acquire on a semaphore to take a token
        The semaphore is use like a mutex one on one
        """
        # Retrieve the active semaphore
        semaphore = self._semaphores.get(
            self.id,
            {}).get(
            warehouse_id,
            {}).get(
            reference_document,
            None)

        # If there is no semaphore, create a new one
        if semaphore is None:
            semaphore = Semaphore()

            # No semaphore for this scenario
            if not self._semaphores.get(id, False):
                self._semaphores[self.id] = {}

            # no semaphore for this scenario in this warehouse
            if not self._semaphores[self.id].get(warehouse_id, False):
                self._semaphores[self.id][warehouse_id] = {}

            # Store the semaphore
            self._semaphores[self.id][warehouse_id][
                reference_document] = semaphore

        # Acquire the mutex
        semaphore.acquire()

    def _semaphore_release(self, warehouse_id, reference_document):
        """
        Make a release on a semaphore to free a token
        The semaphore is use like a mutex one on one
        """
        self._semaphores[self.id][warehouse_id][reference_document].release()


class scanner_scenario_step(models.Model):
    _name = 'scanner.scenario.step'
    _description = 'Step for scenario'

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(
        string='Name',
        size=61,
        required=False,
        help='Name of the step')
    scenario_id = fields.Many2one(
        'scanner.scenario',
        string='Scenario',
        required=True,
        ondelete='cascade',
        help='Scenario for this step')
    step_start = fields.Boolean(
        string='Step start',
        default=False,
        help='Check this if this is the first step of the scenario')
    step_stop = fields.Boolean(
        string='Step stop',
        default=False,
        help='Check this if this is the  last step of the scenario')
    step_back = fields.Boolean(
        string='Step back',
        default=False,
        help='Check this to stop at this step when returning back')
    no_back = fields.Boolean(
        string='No back',
        default=False,
        help='Check this to prevent returning back this step')
    out_transition_ids = fields.One2many(
        'scanner.scenario.transition',
        'from_id',
        string='Outgoing transitons',
        ondelete='cascade',
        help='Transitions which goes to this step')
    in_transition_ids = fields.One2many(
        'scanner.scenario.transition',
        'to_id',
        string='Incoming transitons',
        ondelete='cascade',
        help='Transitions which goes to the next step')
    python_code = fields.Text(
        string='Python code',
        default=PYTHON_CODE_DEFAULT,
        help='Python code to execute')
    reference_res_id = fields.Char(
        string='Reference ID',
        size=64,
        copy=False,
        default=lambda self: uuid.uuid1(),
        required=False,
        readonly=True,
        help='Used by export/import scenario')

    _sql_constraints = [
        ('reference_res_id_uniq',
         'unique (reference_res_id)',
         _('The reference ID of the step must be unique')),
    ]

    @api.model
    def create(self, vals):
        """
        If the reference ID is not in vals, we create it with uuid1
        """
        # Generate a uuid if there is none
        if 'reference_res_id' not in vals:
            vals['reference_res_id'] = uuid.uuid1()

        return super(scanner_scenario_step, self).create(vals=vals)


class scanner_scenario_transition(models.Model):
    _name = 'scanner.scenario.transition'
    _description = 'Transition for scenario'

    _order = 'sequence'

    @api.model
    def _transition_type_get(self):
        return [
            ('scanner', 'Scanner'),
            ('keyboard', 'Keyboard'),
        ]

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(
        string='Name',
        size=64,
        required=True,
        help='Name of the transition')
    sequence = fields.Integer(
        string='Sequence',
        default=0,
        required=False,
        help='Sequence order')
    from_id = fields.Many2one(
        'scanner.scenario.step',
        string='From',
        required=True,
        ondelete='cascade',
        help='Step which launches this transition')
    to_id = fields.Many2one(
        'scanner.scenario.step',
        string='To',
        required=True,
        ondelete='cascade',
        help='Step which is reached by this transition')
    condition = fields.Char(
        string='Condition',
        size=256,
        required=True,
        default='True',
        help='The transition is followed only if this condition is evaluated '
             'as True')
    transition_type = fields.Selection(
        '_transition_type_get',
        string='Transition Type',
        default="scanner",
        help='Type of transition')
    tracer = fields.Char(
        string='Tracer',
        size=12,
        required=False,
        default=False,
        help='Used to determine fron which transition we arrive to the '
             'destination step')
    reference_res_id = fields.Char(
        string='Reference ID',
        size=64,
        copy=False,
        default=lambda self: uuid.uuid1(),
        required=False,
        readonly=True,
        help='Used by export/import scenario')
    scenario_id = fields.Many2one(
        'scanner.scenario',
        string='Scenario',
        required=False,
        related="from_id.scenario_id",
        store=True,
        readonly=True)

    @api.one
    @api.constrains('from_id', 'to_id')
    def _check_scenario(self):
        if self.from_id.scenario_id.id != self.to_id.scenario_id.id:
            raise Warning(_('Error ! You can not create recursive scenarios.'))

        return True

    _sql_constraints = [
        ('reference_res_id_uniq',
         'unique (reference_res_id)',
         _('The reference ID of the transition must be unique')),
    ]

    @api.model
    def create(self, vals):
        """
        If the reference ID is not in vals, we create it with uuid1
        """
        # Generate a uuid if there is none
        if 'reference_res_id' not in vals:
            vals['reference_res_id'] = uuid.uuid1()

        return super(scanner_scenario_transition, self).create(vals=vals)


class scanner_hardware(models.Model):
    _name = 'scanner.hardware'
    _description = 'Scanner Hardware'

    @api.model
    def _colors_get(self):
        return _CURSES_COLORS

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    name = fields.Char(
        string='Name',
        size=128,
        required=True,
        help='Name of the hardware')
    code = fields.Char(
        string='Code',
        size=128,
        required=True,
        help='Code of this hardware')
    log_enabled = fields.Boolean(
        string='Log enabled',
        default=False,
        help='Enable logging messages from scenarios')
    screen_width = fields.Integer(
        string='Screen Width',
        default=20,
        required=False,
        help='Width of the terminal\'s screen')
    screen_height = fields.Integer(
        string='Screen Height',
        default=4,
        required=False,
        help='Height of the terminal\'s screen')
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        required=True,
        ondelete='restrict',
        help='Warehouse where is located this hardware')
    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=False,
        ondelete='restrict',
        help='Allow to define an other user for execute all scenarios with '
             'that scanner instead of default user')
    scenario_id = fields.Many2one(
        'scanner.scenario',
        string='Scenario',
        required=False,
        readonly=True,
        default=False,
        ondelete='restrict',
        help='Scenario used for this hardware')
    step_id = fields.Many2one(
        'scanner.scenario.step',
        string='Current Step',
        required=False,
        readonly=True,
        default=False,
        ondelete='restrict',
        help='Current step for this hardware')
    previous_steps_id = fields.Text(
        string='Previous Step',
        readonly=True,
        help='Previous step for this hardware')
    previous_steps_message = fields.Text(
        string='Previous Message',
        readonly=True,
        help='Previous message for this hardware')
    reference_document = fields.Integer(
        string='Reference',
        default=0,
        required=False,
        readonly=True,
        help='ID of the reference document')
    tmp_val1 = fields.Char(
        'Temp value 1',
        size=256,
        readonly=True,
        help='Temporary value')
    tmp_val2 = fields.Char(
        'Temp value 2',
        size=256,
        readonly=True,
        help='Temporary value')
    tmp_val3 = fields.Char(
        'Temp value 3',
        size=256,
        readonly=True,
        help='Temporary value')
    tmp_val4 = fields.Char(
        'Temp value 4',
        size=256,
        readonly=True,
        help='Temporary value')
    tmp_val5 = fields.Char(
        'Temp value 5',
        size=256,
        readonly=True,
        help='Temporary value')
    base_fg_color = fields.Selection(
        '_colors_get',
        string='Base - Text Color',
        required=True,
        default='white',
        help='Default color for the text')
    base_bg_color = fields.Selection(
        '_colors_get',
        string='Base - Background Color',
        required=True,
        default='blue',
        help='Default color for the background')
    info_fg_color = fields.Selection(
        '_colors_get',
        string='Info - Text Color',
        required=True,
        default='yellow',
        help='Color for the info text')
    info_bg_color = fields.Selection(
        '_colors_get',
        string='Info - Background Color',
        required=True,
        default='blue',
        help='Color for the info background')
    error_fg_color = fields.Selection(
        '_colors_get',
        string='Error - Text Color',
        required=True,
        default='yellow',
        help='Color for the error text')
    error_bg_color = fields.Selection(
        '_colors_get',
        string='Error - Background Color',
        required=True,
        default='red',
        help='Color for the error background')

    @api.model
    def _get_terminal(self, terminal_number):
        terminal = self.search([('code', '=', terminal_number)])
        terminal.ensure_one()
        return terminal

    @logged
    @api.model
    def scanner_check(self, terminal_number):
        terminal = self._get_terminal(terminal_number)
        return terminal.scenario_id and (
            terminal.scenario_id.id,
            terminal.scenario_id.name) or False

    @logged
    @api.model
    def scanner_call(self, terminal_number, action, message=False,
                     transition_type='keyboard'):
        """
        This method is called by the barcode reader,
        """
        # Retrieve the terminal id
        terminal = self._get_terminal(terminal_number)
        # Change uid if defined on the stock scanner
        uid = terminal.user_id.id or self.env.uid
        return terminal.sudo(uid)._scanner_call(
            action, message=message, transition_type=transition_type)

    @api.multi
    def _scanner_call(self, action, message=False,
                      transition_type='keyboard'):
        self.ensure_one()
        scanner_scenario_obj = self.env['scanner.scenario']
        # Retrieve the terminal screen size
        if action == 'screen_size':
            logger.debug('Retrieve screen size')
            screen_size = self._screen_size()
            return ('M', screen_size, 0)

        # Retrieve the terminal screen colors
        if action == 'screen_colors':
            logger.debug('Retrieve screen colors')
            screen_colors = {
                'base': (
                    self.base_fg_color, self.base_bg_color),
                'info': (
                    self.info_fg_color, self.info_bg_color),
                'error': (
                    self.error_fg_color, self.error_bg_color), }
            return ('M', screen_colors, 0)

        # Execute the action
        elif action == 'action':

            # The terminal is attached to a scenario
            if self.scenario_id:
                return self._scenario_save(
                    message,
                    transition_type,
                    scenario_id=self.scenario_id.id,
                    step_id=self.step_id.id,
                    current_object=self.reference_document)
            # We asked for a scan transition type, but no action is running,
            # forbidden
            elif transition_type == 'scanner':
                return self._unknown_action(message)
            # No action to do
            else:
                logger.info('[%s] Action : %s (no current scenario)',
                            self.code, message)
                scenario_ids = scanner_scenario_obj.search(
                    [('name', '=', message),
                     ('type', '=', 'menu'),
                     ('warehouse_ids', 'in', [self.warehouse_id.id])])
                if message == -1:
                    scenario_ids = [False]
                if scenario_ids:
                    scenarios = self._scenario_list(
                        parent_id=scenario_ids.id)
                    if scenarios:
                        menu_name = scenario_ids[0].name
                        return ('L', ['|%s' % menu_name] + scenarios, 0)
                return self._scenario_save(message, transition_type)

        # Reload current step
        elif action == 'restart':
            # The terminal is attached to a scenario
            if self.scenario_id:
                return self._scenario_save(
                    message,
                    'restart',
                    scenario_id=self.scenario_id.id,
                    step_id=self.step_id.id,
                    current_object=self.reference_document)

        # Reload previous step
        elif action == 'back':
            # The terminal is attached to a scenario
            if self.scenario_id:
                return self._scenario_save(
                    message,
                    'back',
                    scenario_id=self.scenario_id.id,
                    step_id=self.step_id.id,
                    current_object=self.reference_document)

        # End required
        elif action == 'end':
            # Empty the values
            logger.info('[%s] End scenario request' % self.code)
            self.empty_scanner_values()

            return ('F', [_('This scenario'), _('is finished')], '')

        # If the terminal is not attached to a scenario, send the menu
        # (scenario list)
        if not self.scenario_id:
            logger.info('[%s] No running scenario' % self.code)
            scenarios = self._scenario_list(message)
            return ('L', scenarios, 0)

        # Nothing matched, return an error
        return self._send_error(['Unknown', 'action'])

    @api.multi
    def _send_error(self, message):
        """
        Sends an error message
        """
        self.ensure_one()
        self.empty_scanner_values()
        return ('R', message, 0)

    def _unknown_action(self, message):
        """
        Sends an unknown action message
        """
        return ('U', message, 0)

    @api.one
    def empty_scanner_values(self):
        """
        This method empty all temporary values, scenario, step and
        reference_document
        Because if we want reset term when error we must use sql query,
        it is bad in production
        """
        scenario_custom_obj = self.env['scanner.scenario.custom']
        if self.scenario_id:
            scenario_custom_obj._remove_values(self.scenario_id, self)

        self.write({
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
        })
        return True

    @api.model
    def scanner_end(self, numterm=None):
        """
        End the end barcode is read, we execute this step
        """
        return self.scanner_call(terminal_number=numterm, action='end')

    @api.multi
    def _memorize(self, scenario_id, step_id, previous_steps_id=False,
                  previous_steps_message=False, obj=None):
        """
        After affect a scenario to a scanner, we must memorize it
        If obj is specify, save it as well (ex: res.partner,12)
        """
        self.ensure_one()
        args = {
            'scenario_id': scenario_id,
            'step_id': step_id,
            'previous_steps_id': previous_steps_id,
            'previous_steps_message': previous_steps_message,
        }
        if obj is not None and isinstance(obj, int):
            args['reference_document'] = obj

        self.write(args)

    @api.multi
    def _do_scenario_save(self, message, transition_type, scenario_id=None,
                          step_id=None, current_object=''):
        """
        Save the scenario on this terminal and execute the current step
        Return the action to the terminal
        """
        self.ensure_one()
        scanner_scenario_obj = self.env['scanner.scenario']
        scanner_step_obj = self.env['scanner.scenario.step']
        terminal = self

        tracer = False

        if (transition_type == 'restart' or
            transition_type == 'back' and
                terminal.scenario_id.id):
            if terminal.step_id.no_back:
                step_id = terminal.step_id.id
            elif terminal.previous_steps_id:
                previous_steps_id = terminal.previous_steps_id.split(',')
                previous_steps_message = terminal.previous_steps_message.split(
                    '\n')
                if not previous_steps_id:
                    return terminal.scanner_end(numterm=terminal.code)

                # Retrieve step id
                step_id = int(previous_steps_id.pop())
                terminal.previous_steps_id = ','.join(previous_steps_id)

                # Retrieve message
                message = eval(previous_steps_message.pop())
                terminal.previous_steps_message = '\n'.join(
                    previous_steps_message)
            else:
                scenario_id = False
                message = terminal.scenario_id.name

        # No scenario in arguments, start a new one
        if not self.scenario_id.id:
            # Retrieve the terminal's warehouse
            terminal_warehouse_ids = terminal.warehouse_id.id
            # Retrieve the warehouse's scenarios
            scenario_ids = []
            if terminal_warehouse_ids:
                scenario_ids = scanner_scenario_obj.search(
                    [('name', '=', message),
                     ('type', '=', 'scenario'),
                     ('warehouse_ids', 'in', [terminal_warehouse_ids])])

            # If at least one scenario was found, pick the start step of the
            # first
            if scenario_ids:
                scenario_id = scenario_ids[0]
                step_ids = scanner_step_obj.search(
                    [('scenario_id', '=', scenario_id.id),
                     ('step_start', '=', True)])

                # No start step found on the scenario, return an error
                if not step_ids:
                    return self._send_error(
                        [_('Please contact'),
                         _('your'),
                         _('administrator'),
                         _('A001')])

                step_id = step_ids[0]

            else:
                return self._send_error([_('Scenario'), _('not found')])

        elif transition_type not in ('back', 'none', 'restart'):
            # Retrieve outgoing transitions from the current step
            scanner_transition_obj = self.pool.get(
                'scanner.scenario.transition')
            transition_ids = scanner_transition_obj.search(
                self.env.cr, self.env.uid, [
                    ('from_id', '=', step_id)], context=self.env.context)
#
#             # Evaluate the condition for each transition
            for transition in scanner_transition_obj.browse(
                    self.env.cr,
                    self.env.uid,
                    transition_ids,
                    context=self.env.context):
                step_id = False
                tracer = ''
                ctx = {
                    'context': self.env.context,
                    'model': self.env[
                        transition.from_id.scenario_id.model_id.model],
                    'cr': self.env.cr,
                    'pool': self.pool,
                    'env': self.env,
                    'uid': self.env.uid,
                    'm': message,
                    'message': message,
                    't': self,
                    'terminal': self,
                }
                try:
                    expr = eval(str(transition.condition), ctx)
                except:
                    logger.exception(
                        "Error when evaluating transition condition /n %s",
                        transition.condition)
                    raise

                # Invalid condition, evaluate next transition
                if not expr:
                    continue

                # Condition passed, go to this step
                step_id = transition.to_id.id
                tracer = transition.tracer

                # Store the old step id if we are on a back step
                if (transition.from_id.step_back and
                        terminal.previous_steps_id.split(
                        ',')[-1] != str(transition.from_id.id)):
                    terminal.previous_steps_message = (
                        terminal.previous_steps_id and '%s\n%s' % (
                            terminal.previous_steps_message, repr(message)) or
                        repr(message))
                    terminal.previous_steps_id = (
                        terminal.previous_steps_id and '%s,%d' % (
                            terminal.previous_steps_id,
                            transition.from_id.id) or
                        str(transition.from_id.id))

                # Valid transition found, stop searching
                break

            # No step found, return an error
            if not step_id:
                terminal.log('No valid transition found !')
                return self._unknown_action(
                    [_('Please contact'), _('your'), _('adminstrator')])

        # Memorize the current step
        if not isinstance(step_id, int):
            step_id = step_id.id

        if not isinstance(scenario_id, int):
            scenario_id = scenario_id.id
        terminal._memorize(
            scenario_id,
            step_id,
            previous_steps_id=terminal.previous_steps_id,
            previous_steps_message=terminal.previous_steps_message,
            obj=current_object)

        scenario_rs = terminal.scenario_id
        try:
            # MUTEX Acquire
            terminal.scenario_id._semaphore_acquire(
                terminal.warehouse_id.id,
                terminal.reference_document or 0)

            # Execute the step
            step = terminal.step_id

            ld = {
                'cr': self.env.cr,
                'uid': self.env.uid,
                'pool': self.pool,
                'env': self.env,
                'model': self.env[step.scenario_id.model_id.model],
                'custom': self.env['scanner.scenario.custom'],
                'term': self,
                'context': self.env.context,
                'm': message,
                'message': message,
                't': terminal,
                'terminal': terminal,
                'tracer': tracer,
                'wkf': workflow,
                'workflow': workflow,
                'scenario': terminal.scenario_id,
            }

            terminal.log('Executing step %d : %s' % (step_id, step.name))
            terminal.log('Message : %s' % repr(message))
            if tracer:
                terminal.log('Tracer : %s' % repr(tracer))

            exec step.python_code in ld
            if step.step_stop:
                terminal.empty_scanner_values()
        except:
            logger.exception('Error when executing code \n, %s',
                             step.python_code)

        scenario_rs._semaphore_release(
            terminal.warehouse_id.id,
            terminal.reference_document or 0)

        return (
            ld.get(
                'act', 'M'), ld.get(
                'res', ['nothing']), ld.get(
                'val', 0))

    @api.multi
    def _scenario_save(self, message, transition_type, scenario_id=None,
                       step_id=None, current_object=None):
        """
        Save the scenario on this terminal, handling transient errors by
        retrying the same step
        Return the action to the terminal
        """
        self.ensure_one()
        result = ('M', ['TEST'], False)
        tries = 0
        current_object = current_object or ''
        while True:
            try:
                result = self._do_scenario_save(
                    message,
                    transition_type,
                    scenario_id=scenario_id,
                    step_id=step_id,
                    current_object=current_object)
                break
            except OperationalError as e:
                # Automatically retry the typical transaction serialization
                # errors
                self.env.cr.rollback()
                if e.pgcode not in PG_CONCURRENCY_ERRORS_TO_RETRY:
                    logger.warning(
                        "[%s] OperationalError",
                        self.code,
                        exc_info=True)
                    result = (
                        'R', [
                            'Please contact', 'your', 'administrator'], 0)
                    break
                if tries >= MAX_TRIES_ON_CONCURRENCY_FAILURE:
                    logger.warning(
                        "[%s] Concurrent transaction - "
                        "OperationalError %s, maximum number of tries reached",
                        self.code,
                        e.pgcode)
                    result = (
                        'E', [
                            ustr('Concurrent transaction - OperationalError '
                                 '%s, maximum number of tries reached') %
                            (e.pgcode)], True)
                    break
                wait_time = random.uniform(0.0, 2 ** tries)
                tries += 1
                logger.info(
                    "[%s] Concurrent transaction detected (%s), "
                    "retrying %d/%d in %.04f sec...",
                    self.code,
                    e.pgcode,
                    tries,
                    MAX_TRIES_ON_CONCURRENCY_FAILURE,
                    wait_time)
                time.sleep(wait_time)
            except (except_orm, Warning) as e:
                # ORM exception, display the error message and require the "go
                # back" action
                self.env.cr.rollback()
                logger.warning('[%s] OSV Exception:', self.code, exc_info=True)
                result = ('E', [e.name, u'', e.value], True)
                break
            except Exception as e:
                self.env.cr.rollback()
                logger.error('[%s] Exception: ', self.code, exc_info=True)
                result = ('R', ['Please contact', 'your', 'administrator'], 0)
                self.empty_scanner_values()
                break
        self.log('Return value : %r' % (result,))

        # Manage automatic steps
        if result[0] == 'A':
            return self.scanner_call('action', message=result[2])

        return result

    @api.model
    def _scenario_list(self, parent_id=False):
        """
        Retrieve the scenario list for this warehouse
        """

        scanner_scenario_obj = self.env['scanner.scenario']
        scanner_scenario_ids = scanner_scenario_obj.search(
            [('warehouse_ids', 'in', [self.warehouse_id.id]),
             ('parent_id', '=', parent_id)])
        return scanner_scenario_ids.mapped('name')

    @api.multi
    def _screen_size(self):
        """
        Retrieve the screen size for this terminal
        """
        self.ensure_one()
        return (self.screen_width, self.screen_height)

    def log(self, log_message):
        if self.log_enabled:
            logger.info('[%s] %s' % (self.code, ustr(log_message)))


class scanner_scenario_custom(models.Model):
    _name = 'scanner.scenario.custom'
    _description = 'Temporary value for scenario'

    _rec_name = "scenario_id"

    # ===========================================================================
    # COLUMNS
    # ===========================================================================
    scenario_id = fields.Many2one(
        'scanner.scenario',
        string='Scenario',
        required=False,
        ondelete='cascade',
        help='Values used for this scenario')
    scanner_id = fields.Many2one(
        'scanner.hardware',
        string='Scanner',
        required=False,
        ondelete='cascade',
        help='Values used for this scanner')
    model = fields.Char(
        string='Model',
        size=255,
        required=True,
        help='Model used for these data')
    res_id = fields.Integer(
        string='Values id',
        default=0,
        required=True,
        help='ID of the model source')
    char_val1 = fields.Char(
        string='Char Value 1',
        size=255,
        default='',
        required=False,
        help='Temporary char value')
    char_val2 = fields.Char(
        string='Char Value 2',
        size=255,
        default='',
        required=False,
        help='Temporary char value')
    char_val3 = fields.Char(
        string='Char Value 3',
        size=255,
        default='',
        required=False,
        help='Temporary char value')
    char_val4 = fields.Char(
        string='Char Value 4',
        size=255,
        default='',
        required=False,
        help='Temporary char value')
    char_val5 = fields.Char(
        string='Char Value 5',
        size=255,
        default='',
        required=False,
        help='Temporary char value')
    int_val1 = fields.Integer(
        string='Int Value 1',
        default=0,
        required=False,
        help='Temporary int value')
    int_val2 = fields.Integer(
        string='Int Value 2',
        default=0,
        required=False,
        help='Temporary int value')
    int_val3 = fields.Integer(
        string='Int Value 3',
        default=0,
        required=False,
        help='Temporary int value')
    int_val4 = fields.Integer(
        string='Int Value 4',
        default=0,
        required=False,
        help='Temporary int value')
    int_val5 = fields.Integer(
        string='Int Value 5',
        default=0,
        required=False,
        help='Temporary int value')
    float_val1 = fields.Float(
        string='Float Value 1',
        default=0.0,
        required=False,
        help='Temporary float value')
    float_val2 = fields.Float(
        string='Float Value 2',
        default=0.0,
        required=False,
        help='Temporary float value')
    float_val3 = fields.Float(
        string='Float Value 3',
        default=0.0,
        required=False,
        help='Temporary float value')
    float_val4 = fields.Float(
        string='Float Value 4',
        default=0.0,
        required=False,
        help='Temporary float value')
    float_val5 = fields.Float(
        string='Float Value 5',
        default=0.0,
        required=False,
        help='Temporary float value')
    text_val = fields.Text(
        string='Text',
        default='',
        required=False,
        help='Temporary text value')

    @api.model
    def _get_domain(self, scenario, scanner):
        """
        Create a domain to find custom values.
        Use the fields shared_custom of scenario and scanner
        """
        # Domain if custom values are shared
        if scenario.shared_custom is True:
            return [
                ('scenario_id', '=', scenario.id),
                ('scanner_id.reference_document', '=',
                 scanner.reference_document),
                ('scanner_id.warehouse_id', '=', scanner.warehouse_id.id)]

        # Default domain
        return [('scenario_id', '=', scenario.id),
                ('scanner_id', '=', scanner.id)]

    @api.model
    def _get_values(self, scenario, scanner, model='', res_id=None,
                    domain=None):
        """
        Returns read customs line
        @param domain : list of tuple for search method
        """
        # Get the default search domain
        search_domain = self._get_domain(scenario, scanner)

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
        ids = self.search(search_domain)

        # If ids were found, return data from these ids
        if ids:
            return self.read(ids, [])

        # No id found, return an empty list
        return []

    @api.model
    def _set_values(self, values):
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
        return self.write(ids, vals)

    @api.model
    def _remove_values(self, scenario, scanner):
        """
        Unlink all the line links from current scenario
        """
        scanner_hardware_obj = self.env['scanner.hardware']
        scanner_ids = []

        # If custom values are shared, search for other hardware using the same
        if scenario.shared_custom is True:
            scanner_ids = scanner_hardware_obj.search(
                [('scenario_id', '=', scenario.id),
                 ('warehouse_id', '=', scanner.warehouse_id.id),
                 ('reference_document', '=', scanner.reference_document),
                 ('id', '!=', scanner.id)])

        # Search for values attached to the current scenario
        values_attached = self.search(
            [('scenario_id', '=', scenario.id),
             ('scanner_id', '=', scanner.id)])

        # If other scanners are on the current scenario, attach the first
        if scanner_ids:
            return values_attached.write({'scanner_id': scanner_ids.id})

        # Else, delete the current custom values
        return values_attached.unlink()
