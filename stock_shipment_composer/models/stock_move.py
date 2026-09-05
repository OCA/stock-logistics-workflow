# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare


class StockMove(models.Model):
    _inherit = "stock.move"

    composer_line_ids = fields.One2many(
        "stock.shipment.composer.line",
        "move_id",
        string="Shipment Composer Lines",
        copy=False,
    )
    shipment_composer_ids = fields.Many2many(
        "stock.shipment.composer",
        string="Shipment Composers",
        compute="_compute_shipment_composer_ids",
    )
    shipment_composer_id = fields.Many2one(
        "stock.shipment.composer",
        copy=False,
        help="Technical field to record the linked shipment composer when composer "
        "is being validated.",
    )
    composer_line_qty = fields.Float(compute="_compute_composer_line_qty", store=True)
    composer_unallocated_qty = fields.Float(
        compute="_compute_composer_line_qty", store=True
    )
    move_split_origin_id = fields.Many2one(
        "stock.move",
        string="Split Origin Move",
        copy=False,
        help="The original move from which this move was split.",
    )

    def _compute_shipment_composer_ids(self):
        for rec in self:
            rec.shipment_composer_ids = rec.composer_line_ids.composer_id

    @api.depends("composer_line_ids.quantity", "composer_line_ids.state")
    def _compute_composer_line_qty(self):
        for rec in self:
            rec.composer_line_qty = sum(
                rec.composer_line_ids.filtered(
                    lambda x: x.state in ["in_progress", "done"]
                ).mapped("quantity")
            )
            rec.composer_unallocated_qty = rec.product_uom_qty - rec.composer_line_qty

    @api.constrains("composer_line_qty", "product_uom_qty", "state")
    def _check_composer_total_qty(self):
        for move in self.filtered(lambda m: m.state not in ("done", "cancel")):
            if (
                float_compare(
                    move.composer_line_qty,
                    move.product_uom_qty,
                    precision_rounding=move.product_uom.rounding,
                )
                > 0
            ):
                raise ValidationError(
                    _(
                        "Total composer quantity (%(line_qty)s) for '%(product)s' "
                        "cannot exceed the move quantity (%(move_qty)s)."
                    )
                    % {
                        "line_qty": move.composer_line_qty,
                        "product": move.product_id.display_name,
                        "move_qty": move.product_uom_qty,
                    }
                )

    @api.model_create_multi
    def create(self, vals_list):
        new_move = super().create(vals_list)
        origin_move = new_move.move_split_origin_id
        if len(new_move) == 1 and origin_move:
            composer_lines = origin_move.composer_line_ids.filtered(
                lambda x: x.state not in ["done", "cancel"]
                and x.composer_id != origin_move.shipment_composer_id
            )
            if composer_lines:
                composer_lines.move_id = new_move
        return new_move

    def _split(self, qty, restrict_partner_id=False):
        res = super()._split(qty, restrict_partner_id=restrict_partner_id)
        if res:
            res[0]["move_split_origin_id"] = self.id
        return res

    def name_get(self):
        res = []
        if not self.env.context.get("is_shipment_composer"):
            return super().name_get()
        for move in self:
            res.append(
                (
                    move.id,
                    "%s%s%s"
                    % (
                        move.picking_id.origin
                        and "%s: " % move.picking_id.origin
                        or "",
                        move.sale_line_id
                        and "%s " % move.sale_line_id.name
                        or move.product_id.display_name
                        or "",
                        "(%s)" % move.composer_unallocated_qty,
                    ),
                )
            )
        return res
