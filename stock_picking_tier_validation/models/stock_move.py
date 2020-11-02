# Copyright 2020 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.constrains("state", "picking_id.review_ids", "picking_id.review_ids.status")
    def _check_tier_review(self):
        tiers = self.env["tier.definition"].search([("model", "=", "stock.picking")])
        for move in self:
            valid_tiers = any([move.picking_id.evaluate_tier(tier) for tier in tiers])
            need_validation = (
                not move.picking_id.review_ids
                and valid_tiers
                and getattr(move.picking_id, move.picking_id._state_field)
                in move.picking_id._state_to
            )
            if (
                move.state in move.picking_id._state_to
                and not move.picking_id.validated
                and need_validation
            ):
                raise ValidationError(_("This picking needs to be validated."))
