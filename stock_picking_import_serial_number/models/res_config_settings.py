# Copyright 2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    default_sn_search_product_by_field = fields.Selection(
        [("default_code", "Reference"), ("barcode", "Barcode")],
        string="Search product by field",
        default="default_code",
        default_model="stock.picking.import.serial.number.wiz",
        required=True,
    )

    default_sn_product_column_index = fields.Integer(
        string="Column index for product",
        default_model="stock.picking.import.serial.number.wiz",
        default=0,
    )
    default_sn_serial_column_index = fields.Integer(
        string="Column index for S/N",
        default_model="stock.picking.import.serial.number.wiz",
        default="1",
    )
