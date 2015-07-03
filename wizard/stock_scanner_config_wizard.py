# -*- coding: utf-8 -*-
from openerp import models, api, fields

ACTIVABLE_XML_IDS = [
    'stock_scanner.hardware_reset_user_id_on_timeout',
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
