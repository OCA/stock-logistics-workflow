# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockLandedCost(models.Model):
    _inherit = "stock.landed.cost"

    purchase_id = fields.Many2one(comodel_name="purchase.order", string="Purchase")
