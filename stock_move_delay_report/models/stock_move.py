# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    date_delay = fields.Float(
        compute="_compute_date_delay",
        store=True,
        help="If the move is done, the difference between "
        "the scheduled date and the deadline",
    )

    responsible_id = fields.Many2one(
        comodel_name="res.partner",
        compute="_compute_responsible",
        store=True,
        help="Partner responsible of completing the move on time.",
    )

    @api.depends("state")
    def _compute_date_delay(self):
        for rec in self:
            if rec.state == "done" and rec.date_expected:
                rec.date_delay = (rec.date - rec.date_expected).days
            elif not rec.date_expected:
                rec.date_delay = 0
            else:
                rec.date_delay = None

    def _compute_responsible(self):
        for rec in self:
            if rec.picking_id.picking_type_id.code == "incoming":
                rec.responsible_id = rec.picking_id.partner_id
            elif rec.picking_id.picking_type_id.code == "outgoing":
                rec.responsible_id = rec.picking_id.company_id.partner_id
