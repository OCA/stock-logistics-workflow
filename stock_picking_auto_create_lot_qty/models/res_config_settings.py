# Copyright Cetmix OU 2024
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    stock_lot_serial_sequence_id = fields.Many2one(
        string="Sequences",
        related="company_id.stock_lot_serial_sequence_id",
        readonly=False,
    )
