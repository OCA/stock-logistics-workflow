# Copyright 2022 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    picking_type_warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        string="Stock picking type warehouse",
        related="picking_type_id.warehouse_id",
    )


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.onchange("product_id")
    def _onchange_product_id(self):
        """Avoid calling product name_get method several times
        with 'sp_product_stock_inline' context key.
        """
        sp_line = self
        if self.env.context.get("sp_product_stock_inline"):
            sp_line = self.with_context(
                sp_product_stock_inline=False, warehouse=self.warehouse_id.id
            )
        return super(StockMove, sp_line)._onchange_product_id()


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    picking_type_warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        string="Stock picking type warehouse",
        related="picking_id.picking_type_id.warehouse_id",
    )

    @api.onchange("product_id")
    def _onchange_product_id(self):
        """Avoid calling product name_get method several times
        with 'sp_product_stock_inline' context key.
        """
        sp_line = self
        if self.env.context.get("sp_product_stock_inline"):
            sp_line = self.with_context(
                sp_product_stock_inline=False,
                warehouse=self.picking_type_warehouse_id.id,
            )
        return super(StockMoveLine, sp_line)._onchange_product_id()
