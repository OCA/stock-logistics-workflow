# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, api, fields, models


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
        compute="_compute_revert_landed_cost_count", store=True
    )

    @api.depends("revert_landed_cost_ids")
    def _compute_revert_landed_cost_count(self):
        for landed_cost in self:
            landed_cost.revert_landed_cost_count = len(
                landed_cost.revert_landed_cost_ids
            )

    def revert_landed_costs(self):
        for landed_cost in self:
            revert_landed_cost = landed_cost.copy(
                {
                    "state": "draft",
                    "picking_ids": landed_cost.picking_ids.ids,
                    "vendor_bill_id": landed_cost.vendor_bill_id.id,
                    "cost_lines": [
                        Command.clear(),
                        *[
                            Command.create(
                                {
                                    "product_id": line.product_id.id,
                                    "name": line.name,
                                    "account_id": line.account_id.id,
                                    "price_unit": -line.price_unit,
                                    "split_method": line.split_method,
                                }
                            )
                            for line in landed_cost.cost_lines
                        ],
                    ],
                }
            )
            landed_cost.revert_landed_cost_ids = [Command.link(revert_landed_cost.id)]
            return self.with_context(
                revert_landed_cost_id=revert_landed_cost.id
            ).action_view_revert_landed_cost()

    def action_view_revert_landed_cost(self):
        domain = [("id", "in", self.revert_landed_cost_ids.ids)]
        if self.env.context.get("revert_landed_cost_id"):
            domain = [("id", "=", self.env.context.get("revert_landed_cost_id"))]
        return {
            "name": "Revert Landed Costs",
            "view_type": "form",
            "view_mode": "tree,form,kanban",
            "res_model": "stock.landed.cost",
            "type": "ir.actions.act_window",
            "domain": domain,
        }
