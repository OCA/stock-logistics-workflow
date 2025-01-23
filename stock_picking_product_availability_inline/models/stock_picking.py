# Copyright 2022 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    picking_type_warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        string="Stock picking type warehouse",
        related="picking_type_id.warehouse_id",
    )


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    picking_type_warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        string="Stock picking type warehouse",
        related="picking_id.picking_type_id.warehouse_id",
    )
