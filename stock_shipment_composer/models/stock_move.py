# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
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

    @api.depends("composer_line_ids.composer_id")
    def _compute_shipment_composer_ids(self):
        for rec in self:
            rec.shipment_composer_ids = rec.composer_line_ids.composer_id

    @api.depends(
        "product_uom_qty", "composer_line_ids.quantity", "composer_line_ids.state"
    )
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
        if self.env.context.get("skip_composer_qty_check"):
            return
        for move in self.filtered(lambda m: m.state not in ("done", "cancel")):
            if not move.composer_line_ids:
                continue
            # POs with negative quantities (e.g., returns) get bitten at confirm without
            # this condition, as a move is temporarily created with a negative qty
            if not move.composer_line_qty or move.product_uom_qty < 0:
                continue
            if (
                float_compare(
                    move.composer_line_qty,
                    move.product_uom_qty,
                    precision_rounding=move.product_uom.rounding,
                )
                > 0
            ):
                raise ValidationError(
                    self.env._(
                        "Total composer quantity (%(line_qty)s) for '%(product)s' "
                        "cannot exceed the move quantity (%(move_qty)s).",
                        line_qty=move.composer_line_qty,
                        product=move.product_id.display_name,
                        move_qty=move.product_uom_qty,
                    )
                )

    @api.model_create_multi
    def create(self, vals_list):
        new_moves = super().create(vals_list)
        for new_move in new_moves.filtered("move_split_origin_id"):
            origin_move = new_move.move_split_origin_id
            composer_lines = (
                origin_move.composer_line_ids
                - origin_move.shipment_composer_id.line_ids
            ).filtered(lambda x: x.state not in ["done", "cancel"])
            for line in composer_lines:
                line.write({"move_id": new_move.id, "quantity": line.quantity})
        return new_moves

    def _split(self, qty, restrict_partner_id=False):
        if not self.env.context.get("validated_by_composer"):
            return super()._split(qty, restrict_partner_id=restrict_partner_id)
        res = super(StockMove, self.with_context(skip_composer_qty_check=True))._split(
            qty, restrict_partner_id=restrict_partner_id
        )
        if res:
            res[0]["move_split_origin_id"] = self.id
        return res

    def _action_done(self, cancel_backorder=False):
        composer_id = self.env.context.get("validated_by_composer")
        if cancel_backorder and composer_id:
            other_lines = self.composer_line_ids.filtered(
                lambda x: x.composer_id.id != composer_id
                and x.state not in ["done", "cancel"]
            )
            if other_lines:
                raise UserError(
                    self.env._(
                        "You cannot validate without a backorder while other shipment "
                        "composers (%(composers)s) have open lines on the same "
                        "moves. Cancel or adjust them first.",
                        composers=", ".join(other_lines.composer_id.mapped("name")),
                    )
                )
        return super()._action_done(cancel_backorder=cancel_backorder)

    @api.depends_context("is_shipment_composer")
    @api.depends(
        "picking_id.origin",
        "product_id.display_name",
        "composer_unallocated_qty",
    )
    def _compute_display_name(self):
        if not self.env.context.get("is_shipment_composer"):
            return super()._compute_display_name()
        for move in self:
            sale_line = self._fields.get("sale_line_id") and move.sale_line_id
            origin = f"{move.picking_id.origin}: " if move.picking_id.origin else ""
            label = (
                f"{sale_line.name} "
                if sale_line
                else (move.product_id.display_name or "")
            )
            move.display_name = f"{origin}{label}({move.composer_unallocated_qty})"
