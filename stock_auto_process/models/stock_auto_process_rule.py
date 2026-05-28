# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools.safe_eval import safe_eval


class StockAutoProcessRule(models.Model):
    _name = "stock.auto.process.rule"
    _description = "Stock Auto Process Rule"
    _order = "sequence, id"
    _check_company_auto = True

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    picking_type_ids = fields.Many2many(
        "stock.picking.type",
        string="Operation Types",
        help="If set, only pickings of these operation types are processed. "
        "Leave empty to apply to any operation type.",
    )
    domain = fields.Char(
        default="[]",
        help="Additional domain on stock.picking used to refine selection.",
    )
    do_confirm = fields.Boolean(string="Auto Confirm")
    do_assign = fields.Boolean(string="Auto Assign", default=True)
    do_validate = fields.Boolean(string="Auto Validate", default=True)
    create_backorder = fields.Boolean(
        default=True,
        help="When auto-validating a partially available picking, controls "
        "what happens to the unfulfilled quantity. "
        "If enabled, a backorder picking is created for the remainder. "
        "If disabled, the picking is validated as-is and the unfulfilled "
        "quantity is discarded (no backorder).",
    )

    def _get_candidate_states(self):
        self.ensure_one()
        states = set()
        if self.do_confirm:
            states.add("draft")
        if self.do_assign:
            states.update(("confirmed", "partially_available"))
        if self.do_validate:
            states.update(("assigned", "partially_available"))
        return list(states)

    def _get_picking_domain(self):
        self.ensure_one()
        states = self._get_candidate_states()
        if not states:
            return [("id", "=", 0)]
        domain = [
            ("state", "in", states),
            ("company_id", "=", self.company_id.id),
        ]
        if self.picking_type_ids:
            domain.append(("picking_type_id", "in", self.picking_type_ids.ids))
        if self.domain:
            domain += safe_eval(self.domain)
        return domain

    def _search_pickings(self):
        self.ensure_one()
        return self.env["stock.picking"].search(self._get_picking_domain())
