# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, fields, models


class StockLandedCost(models.Model):
    _inherit = "stock.landed.cost"

    landed_cost_id = fields.Many2one(
        comodel_name="stock.landed.cost",
        string="Landed Cost Origin",
    )
    revert_landed_cost_ids = fields.One2many(
        comodel_name="stock.landed.cost",
        inverse_name="landed_cost_id",
    )
    revert_landed_cost_count = fields.Integer(
        compute="_compute_revert_landed_cost_count"
    )

    def _compute_revert_landed_cost_count(self):
        counts = dict(
            self._read_group(
                [("landed_cost_id", "in", self.ids)],
                groupby=["landed_cost_id"],
                aggregates=["__count"],
            )
        )
        for landed_cost in self:
            landed_cost.revert_landed_cost_count = counts.get(landed_cost, 0)

    def _prepare_revert_cost_line_vals(self, line):
        return {
            "product_id": line.product_id.id,
            "name": line.name,
            "account_id": line.account_id.id,
            "price_unit": -line.price_unit,
            "split_method": line.split_method,
        }

    def _prepare_revert_landed_cost_vals(self):
        self.ensure_one()
        return {
            "state": "draft",
            "landed_cost_id": self.id,
            "picking_ids": self.picking_ids.ids,
            "vendor_bill_id": self.vendor_bill_id.id,
            "cost_lines": [
                Command.clear(),
                *[
                    Command.create(self._prepare_revert_cost_line_vals(line))
                    for line in self.cost_lines
                ],
            ],
        }

    def revert_landed_costs(self):
        self.ensure_one()
        revert_landed_cost = self.copy(self._prepare_revert_landed_cost_vals())
        return self.action_view_revert_landed_cost(revert_landed_cost)

    def action_view_revert_landed_cost(self, revert_landed_costs=False):
        self.ensure_one()
        revert_landed_costs = revert_landed_costs or self.revert_landed_cost_ids
        return {
            "name": "Revert Landed Costs",
            "view_type": "form",
            "view_mode": "tree,form,kanban",
            "res_model": "stock.landed.cost",
            "type": "ir.actions.act_window",
            "domain": [("id", "in", revert_landed_costs.ids)],
        }
