# Copyright Cetmix OU 2024
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    stock_lot_serial_sequence_id = fields.Many2one(
        "ir.sequence",
        default=lambda self: self.env.ref(
            "stock.sequence_production_lots", raise_if_not_found=False
        ),
    )
