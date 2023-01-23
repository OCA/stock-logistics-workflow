# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    is_priority_editable = fields.Boolean(
        compute="_compute_is_priority_editable",
    )
    priority = fields.Selection(
        inverse="_inverse_priority",
        readonly=False,
    )

    @api.depends("company_id.stock_move_manage_priority", "is_locked", "state")
    def _compute_is_priority_editable(self):
        user_has_group = self.env.user.has_group(
            "stock_move_manage_priority.group_stock_move_priority_manager"
        )
        for rec in self:
            rec.is_priority_editable = (
                user_has_group
                and not rec.is_locked
                and rec.state not in ("done", "cancel")
                and rec.company_id.stock_move_manage_priority
            )

    def _inverse_priority(self):
        for rec in self:
            if not rec.is_priority_editable:
                rec.priority = rec.picking_id.priority if rec.picking_id else "0"
