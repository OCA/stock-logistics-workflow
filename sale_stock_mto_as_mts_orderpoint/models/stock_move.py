# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class StockMove(models.Model):

    _inherit = "stock.move"

    is_from_mto_route = fields.Boolean(compute="_compute_is_from_mto_route")

    def _compute_is_from_mto_route(self):
        mto_route = self.env.ref("stock.route_warehouse0_mto", raise_if_not_found=False)
        if not mto_route:
            self.update({"is_from_mto_route": False})
        else:
            for move in self:
                move.is_from_mto_route = move.rule_id.route_id == mto_route
