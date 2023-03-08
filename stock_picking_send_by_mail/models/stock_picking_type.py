# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    send_delivery_email = fields.Boolean(
        string="Send Delivery E-mail",
        help="Send an e-mail on validation to the customer with the delivery slip.",
        default=False,
    )
