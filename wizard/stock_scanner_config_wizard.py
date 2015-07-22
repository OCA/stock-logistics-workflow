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
from openerp import models, api, fields

ACTIVABLE_XML_IDS = [
    'stock_scanner.hardware_reset_user_id_on_timeout',
    'stock_scanner.scanner_scenario_login',
    'stock_scanner.scanner_scenario_logout',
]


class StockScannerConfigWizard(models.TransientModel):
    _name = 'stock.scanner.config.wizard'
    _description = 'Stock scanner module configuration'

    is_login_enabled = fields.Boolean(
        'Login/logout scenarii enabled',
        default=lambda self: self.env.ref(
            ACTIVABLE_XML_IDS[0]).active)

    session_timeout_delay = fields.Integer(
        'Session validity in seconds',
        default=lambda self: self.env.ref(
                'stock_scanner.hardware_scanner_session_timeout_sec').value)

    @api.one
    def apply_config(self):
        self.ensure_one()
        for xml_id in ACTIVABLE_XML_IDS:
            self.env.ref(xml_id).active = self.is_login_enabled

        self.env['ir.config_parameter'].set_param(
            'hardware_scanner_session_timeout', self.session_timeout_delay)
