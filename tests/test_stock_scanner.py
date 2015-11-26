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
import datetime

from openerp import _, fields
from openerp.tests import common


class TestStockScanner(common.TransactionCase):

    def test_scanner_call(self):
        scanner_hardware_1 = self.browse_ref(
            'stock_scanner.scanner_hardware_1')

        # Reset the current scenario
        # just in case the database has been manually used
        scanner_hardware_1.empty_scanner_values()

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
        self.assertEquals(('M', {
            'base': ('white', 'blue'),
            'error': ('yellow', 'red'),
            'info': ('yellow', 'blue'),
        }, 0), ret)

        #  a call without action will return the list of root scenario
        scanner_scenario_menu_tutorial = self.browse_ref(
            'stock_scanner.scanner_scenario_tutorial')
        ret = scanner_hardware.scanner_call(code, action=None)
        self.assertEquals(('L', ['Tutorial', 'Stock', 'Tests'], 0), ret)

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
            ('L', ['|' + 'Tutorial',
                   'Step types', 'Sentinel'], 0), ret)

        # when we select a scenario of type scenario,
        # the scenario is linked to the hardware
        ret = scanner_hardware.scanner_call(
            code, action='action',
            message=scanner_scenario_step_types.name)

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
            'stock_scanner.scanner_scenario_step_step_types_introduction')
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
            'stock_scanner.scanner_scenario_step_step_types_message')
        self.assertEquals(
            scanner_hardware_1.step_id,
            scanner_scenario_step_types_message_step)

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
            'stock_scanner.scanner_scenario_step_step_types_list')
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
        self.assertEquals(('L', ['Tutorial', 'Stock', 'Tests'], 0), ret)

    def test_login_logout(self):
        demo_uid = self.ref('base.user_demo')
        user_demo = self.browse_ref('base.user_demo')
        sentinel_uid = self.ref('stock_scanner.user_sentinel')
        scanner_scenario_login = self.browse_ref(
            'stock_scanner.scanner_scenario_login')
        scanner_scenario_logout = self.browse_ref(
            'stock_scanner.scanner_scenario_logout')
        scanner_scenario = self.env['scanner.scenario']
        # by default the login/logout scenarii are hidden
        res = scanner_scenario.search(
            [('id', 'in', (scanner_scenario_login.id,
                           scanner_scenario_logout.id))])
        self.assertFalse(res)

        # a cron used to manage the timeout of the session on the scanner
        # hardware is also disabled by default
        hardware_reset_user_id_on_timeout = self.browse_ref(
            'stock_scanner.hardware_reset_user_id_on_timeout')
        self.assertFalse(hardware_reset_user_id_on_timeout.active)

        # the demo scenario is available to users members of
        # stock.group_stock_user as previously
        scanner_hardware_1 = self.browse_ref(
            'stock_scanner.scanner_hardware_1')

        # Reset the current scenario
        # just in case the database has been manually used
        scanner_hardware_1.empty_scanner_values()

        code = scanner_hardware_1.code
        scanner_hardware = self.env['scanner.hardware']
        ret = scanner_hardware.sudo(demo_uid).scanner_call(code, action=None)
        self.assertEquals(('L', ['Tutorial', 'Stock', 'Tests'], 0), ret)
        # The technical user to use by sentinel when using the login/logout
        # functionality show nothings
        ret = scanner_hardware.sudo(sentinel_uid).scanner_call(code,
                                                               action=None)
        self.assertEquals(('L', [], 0), ret)
        # The login/lgout functionnality can be enabled by a configuration
        wizard = self.env['stock.config.settings'].create(
            {'is_login_enabled': True})
        wizard.execute()
        # when the config is applied, the cron and the 2 dedicated scenarii
        # become actives
        self.assertTrue(hardware_reset_user_id_on_timeout.active)
        res = scanner_scenario.search(
            [('id', 'in', (scanner_scenario_login.id,
                           scanner_scenario_logout.id))])
        self.assertEquals(2, len(res))

        # Once the functionality is enabled, the sentinel user show the login
        # scenario if not yer logged in
        scanner_hardware = scanner_hardware.sudo(sentinel_uid)
        ret = scanner_hardware.scanner_call(code, action=None)
        self.assertEquals(('L', [scanner_scenario_login.name], 0), ret)

        # Let's start the login scenario
        ret = scanner_hardware.scanner_call(
            code, action='action',
            message=scanner_scenario_login.name)
        # The first step is to enter the login name
        self.assertEquals(('T', ['Login ?'], 0), ret)
        ret = scanner_hardware.scanner_call(
            code, action='action', message=user_demo.login,
            transition_type='keyboard')
        # The second step is to enter the pwd
        self.assertEquals(('T', ['| Login demo', 'Pwd ?'], 0), ret)
        # If we give a wrong password an error message is displayed
        ret = scanner_hardware.scanner_call(
            code, action='action', message='wrong',
            transition_type='keyboard')
        self.assertEquals(('E', ['Wrong login/password'], True), ret)

        # And the step back is to return on the first step
        ret = scanner_hardware.scanner_call(
            code, action='back', message='',
            transition_type='keyboard')
        self.assertEquals(('T', ['Login ?'], 0), ret)
        # we enter the login
        ret = scanner_hardware.scanner_call(
            code, action='action',
            message=user_demo.login)
        # and the right pwd
        ret = scanner_hardware.scanner_call(
            code, action='action',
            message=user_demo.password)
        # now we are logged in
        self.assertEquals(('F', ['You are now authenticated as demo !'], 0),
                          ret)
        # once we are logged in, the hardware display the available scenarii
        # including the logout one
        ret = scanner_hardware.scanner_call(
            code, action='menu', message=None,
            transition_type='keyboard')
        self.assertEquals(('L', [
            'Tutorial',
            'Stock',
            'Tests',
            'Logout',
        ], 0), ret)

        # if we logout, only the login scenario will be displayed again
        ret = scanner_hardware.scanner_call(
            code, action='action', message=scanner_scenario_logout.name,
            transition_type='keyboard')
        self.assertEquals(
            ('C', ['', 'Do you really want to logout?'], 0), ret)
        ret = scanner_hardware.scanner_call(
            code, action='action', message=True,
            transition_type='keyboard')
        self.assertEquals(
            ('F', ['You are now logged out', 'Bye !'], 0), ret)
        ret = scanner_hardware.scanner_call(
            code, action='menu', message=None,
            transition_type='keyboard')
        self.assertEquals(('L', [scanner_scenario_login.name], 0), ret)

    def test_login_timeout(self):
        """Test the wizard used to reset the user on the hardware when
        time is out"""
        # The login/lgout functionnality can be enabled by configuration.
        wizard = self.env['stock.config.settings'].create(
            {'is_login_enabled': True})
        wizard.execute()
        scanner_hardware_1 = self.browse_ref(
            'stock_scanner.scanner_hardware_1')

        # Reset the current scenario
        # just in case the database has been manually used
        scanner_hardware_1.empty_scanner_values()

        # before login user_id and last_call_dt are empty
        self.assertFalse(scanner_hardware_1.user_id)
        self.assertFalse(scanner_hardware_1.last_call_dt)

        # login the user using the function on the hardware
        user_demo = self.browse_ref('base.user_demo')
        scanner_hardware_1.login(user_demo.login, 'demo')

        # when logged in the user_id and last_call_dt are no longer empty
        self.assertTrue(scanner_hardware_1.user_id)
        self.assertTrue(scanner_hardware_1.last_call_dt)

        # a call to the function called by the cron has no impact if the
        # session is not timed out
        scanner_hardware_1.timeout_session()
        self.assertTrue(scanner_hardware_1.user_id)
        self.assertTrue(scanner_hardware_1.last_call_dt)

        # we update the last_call_dt with an older value to simulate
        # the elapsed time without activity
        timeout_last_call_td = fields.Datetime.from_string(
            scanner_hardware_1.last_call_dt) - datetime.timedelta(
                wizard.session_timeout_delay + 1)
        scanner_hardware_1.last_call_dt = fields.Datetime.to_string(
            timeout_last_call_td)

        # a new call to the session timeout will reset the connected user
        scanner_hardware_1.timeout_session()
        self.assertFalse(scanner_hardware_1.user_id)
        self.assertFalse(scanner_hardware_1.last_call_dt)
