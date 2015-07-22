# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Laurent Mignon
#    Copyright (c) 2015 Acsone SA/NV (http://www.acsone.eu)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import _
from openerp.tests import common


class TestStockScanner(common.TransactionCase):

    def setUp(self):
        common.TransactionCase.setUp(self)

    def test_scanner_call(self):
        scanner_hardware_1 = self.browse_ref(
            'stock_scanner.scanner_hardware_1')
        # By default a scanner is not associated to a user
        self.assertFalse(scanner_hardware_1.user_id)
        # nor to a scenario
        self.assertFalse(scanner_hardware_1.scenario_id)
        # nor a step
        self.assertFalse(scanner_hardware_1.step_id)

        # call to the scanner are done on the model using the scanner code
        scanner_hardware = self.env['scanner.hardware']
        code = scanner_hardware_1.code

        # call action screen_size
        ret = scanner_hardware.scanner_call(code, action='screen_size')
        self.assertEquals(('M', (40, 20), 0), ret)

        # call to screen_color
        ret = scanner_hardware.scanner_call(code, action='screen_colors')
        self.assertEquals(('M', {'base': (u'white', u'blue'),
                                 'error': (u'yellow', u'red'),
                                 'info': (u'yellow', u'blue')}, 0),
                          ret)

        #  a call without action will return the list of root scenario
        scanner_scenario_menu_tutorial = self.browse_ref(
            'stock_scanner.scanner_scenario_menu_tutorial')
        ret = scanner_hardware.scanner_call(code, action=None)
        self.assertEquals(('L', [scanner_scenario_menu_tutorial.name], 0), ret)

        # to select a menu we call the hardware whith action = action and
        # message = name of the menu to select
        ret = scanner_hardware.scanner_call(
            code, action='action',
            message=scanner_scenario_menu_tutorial.name)

        # the result is the list of nested scenario since or scenario is a
        # menu with the parent menu as title
        scanner_scenario_step_types = self.browse_ref(
            'stock_scanner.scanner_scenario_step_types')

        self.assertEquals(
            ('L', ['|' + scanner_scenario_menu_tutorial.name,
                   scanner_scenario_step_types.name], 0), ret)

        # when we select a scenario of type scenario,
        # the scenario is linked to the hardware
        ret = scanner_hardware.scanner_call(
            code, action='action',
            message=scanner_scenario_step_types.name)

        print ret
        self.assertEqual(scanner_hardware_1.scenario_id,
                         scanner_scenario_step_types)

        # the result is the first step to execute
        self.assertEquals(('M',
                           ['|Introduction',
                            '',
                            'Welcome on the stock_scanner module.',
                            '',
                            'This scenario will explain all step types.'],
                           0), ret)
        # and the current step is saved on the hardware
        scanner_scenario_step_types_intro_step = self.browse_ref(
            'stock_scanner.scanner_scenario_step_types_intro_step')
        self.assertEquals(
            scanner_hardware_1.step_id,
            scanner_scenario_step_types_intro_step)

        # a step is executed by calling an action with a transition_type
        ret = scanner_hardware.scanner_call(
            code, action='action', message='',
            transition_type='keyboard')
        # the result is the next step to execute
        self.assertEquals(('M',
                           ['|Message step',
                            '',
                            'A step designed to display some information, '
                            'without waiting for any user input.'],
                           0), ret)

        scanner_scenario_step_types_message_step = self.browse_ref(
            'stock_scanner.scanner_scenario_step_types_message_step')
        self.assertEquals(
            scanner_hardware_1.step_id,
            scanner_scenario_step_types_message_step)

        self.assertEquals(
            scanner_hardware_1.previous_steps_id,
            '%s' % scanner_scenario_step_types_intro_step.id)

        # a back action reset the scenario to the previous_step
        ret = scanner_hardware.scanner_call(
            code, action='back', message='',
            transition_type='keyboard')
        self.assertEquals(('M',
                           ['|Introduction',
                            '',
                            'Welcome on the stock_scanner module.',
                            '',
                            'This scenario will explain all step types.'],
                           0), ret)
        # execute the 2 next steps
        ret = scanner_hardware.scanner_call(
            code, action='action', message='',
            transition_type='keyboard')
        self.assertEquals(
            scanner_hardware_1.step_id,
            scanner_scenario_step_types_message_step)

        scanner_hardware.scanner_call(
            code, action='action', message='',
            transition_type='keyboard')
        scanner_scenario_step_types_list_step = self.browse_ref(
            'stock_scanner.scanner_scenario_step_types_list_step')
        self.assertEquals(
            scanner_hardware_1.step_id,
            scanner_scenario_step_types_list_step)

        # at end of the scenario, the action end is called by the hardware
        ret = scanner_hardware.scanner_call(
            code, action='end', message='',
            transition_type='keyboard')
        # and a message is returned to the hardware
        self.assertEquals(('F', [_('This scenario'), _('is finished')], ''),
                          ret)
        self.assertFalse(scanner_hardware_1.scenario_id)
        self.assertFalse(scanner_hardware_1.step_id)

        # the next call to the parser return the available scenarii
        ret = scanner_hardware.scanner_call(code, action=None)
        self.assertEquals(('L', [scanner_scenario_menu_tutorial.name], 0), ret)
