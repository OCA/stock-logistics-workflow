# -*- coding: utf-8 -*-
# © 2015 Laurent Mignon <laurent.mignon@acsone.eu>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields

ACTIVABLE_XML_IDS = [
    'stock_scanner.hardware_reset_user_id_on_timeout',
    'stock_scanner.scanner_scenario_login',
    'stock_scanner.scanner_scenario_logout',
]


class StockConfig(models.TransientModel):
    """Add options to configure login/logout on scanner"""
    _inherit = 'stock.config.settings'

    is_login_enabled = fields.Boolean('Login/logout scenarii enabled')
    session_timeout_delay = fields.Integer('Session validity in seconds')

    @api.multi
    def get_default_scanner_config(self, fields):
        is_login_enabled = self.env.ref(ACTIVABLE_XML_IDS[0]).active
        session_timeout_delay = self.env.ref(
            'stock_scanner.hardware_scanner_session_timeout_sec').value
        return {'is_login_enabled': is_login_enabled,
                'session_timeout_delay': int(session_timeout_delay)}

    @api.multi
    def set_default_scanner_config(self):
        for xml_id in ACTIVABLE_XML_IDS:
            self.env.ref(xml_id).active = self.is_login_enabled

        self.env['ir.config_parameter'].set_param(
            'hardware_scanner_session_timeout', self.session_timeout_delay)
