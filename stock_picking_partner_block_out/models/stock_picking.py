# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockPicking(models.Model):

    _inherit = "stock.picking"

    partner_picking_block_out = fields.Boolean(
        related="partner_id.picking_block_out", store=True
    )

    @api.constrains("partner_picking_block_out", "state")
    def _check_partner_picking_block_out(self):
        for rec in self:
            if (
                rec.state == "done"
                and rec.partner_picking_block_out
                and rec._is_to_external_location()
            ):
                raise ValidationError(
                    _(
                        "You cannot validate this delivery"
                        " because deliveries to %s are blocked",
                        rec.partner_id.name,
                    )
                )

    @api.depends("partner_picking_block_out")
    def _compute_show_validate(self):
        ret = super()._compute_show_validate()

        for rec in self:
            if rec.partner_picking_block_out:
                rec.show_validate = False

        return ret
