# Copyright 2015 AvanzOSC - Alfredo de la Fuente
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    client_order_ref = fields.Char(
        string="Customer Reference",
        related="sale_id.client_order_ref",
        store=True)
