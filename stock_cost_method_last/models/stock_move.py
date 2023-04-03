# Copyright 2016-2022 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def product_price_update_before_done(self, forced_qty=None):
        super().product_price_update_before_done(forced_qty=forced_qty)
        for move in self.filtered(
            lambda move: move._is_in()
            and move.with_company(move.company_id.id).product_id.cost_method == "last"
        ):
            move.product_id.with_company(move.company_id.id).with_context(
                disable_auto_svl=True
            ).sudo().write({"standard_price": move._get_price_unit()})
