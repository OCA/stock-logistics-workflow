# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare

EDITABLE_STATES = ("confirmed", "in_transit")


class StockInterwarehouseTransferLine(models.Model):
    _name = "stock.interwarehouse.transfer.line"
    _description = "Inter-Warehouse Transfer Line"

    transfer_id = fields.Many2one(
        "stock.interwarehouse.transfer",
        required=True,
        ondelete="cascade",
    )
    product_id = fields.Many2one(
        "product.product", required=True, domain=[("type", "!=", "service")]
    )
    product_uom_qty = fields.Float(
        string="Quantity",
        default=1.0,
        required=True,
    )
    product_uom = fields.Many2one(
        "uom.uom",
        string="Unit of Measure",
        compute="_compute_product_uom",
        store=True,
        precompute=True,
        readonly=False,
    )
    move_ids = fields.One2many(
        "stock.move",
        "interwh_transfer_line_id",
        string="Stock Moves",
    )
    state = fields.Selection(related="transfer_id.state")
    qty_shipped = fields.Float(
        string="Shipped",
        compute="_compute_qty_progress",
        digits="Product Unit of Measure",
    )
    qty_received = fields.Float(
        string="Received",
        compute="_compute_qty_progress",
        digits="Product Unit of Measure",
    )

    # === COMPUTE METHODS ===

    @api.depends("product_id")
    def _compute_product_uom(self):
        for line in self:
            line.product_uom = line.product_id.uom_id

    @api.depends("move_ids.state", "move_ids.quantity", "move_ids.product_uom")
    def _compute_qty_progress(self):
        for line in self:
            line.qty_shipped = line._get_stage_done_qty("outgoing")
            line.qty_received = line._get_stage_done_qty("incoming")

    # === CHECK METHODS ===

    def _check_editable(self):
        for line in self:
            if line.transfer_id.state in ("done", "cancelled"):
                raise UserError(
                    _(
                        "Transfer %(transfer)s is done or cancelled, its products "
                        "can no longer be modified.",
                        transfer=line.transfer_id.name,
                    )
                )

    def _check_stage_decrease(self, stage, qty):
        self.ensure_one()
        rounding = self.product_uom.rounding
        if float_compare(qty, 0.0, precision_rounding=rounding) >= 0:
            return
        open_qty = self._get_stage_open_qty(stage)
        if float_compare(-qty, open_qty, precision_rounding=rounding) <= 0:
            return
        raise UserError(
            _(
                "The quantity of %(product)s cannot be decreased below the quantity "
                "already processed. Instead, create a return in your inventory.",
                product=self.product_id.display_name,
            )
        )

    # === CRUD METHODS ===

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._check_editable()
        lines._sync_stage_moves()
        return lines

    def write(self, vals):
        if "product_uom_qty" in vals:
            self._check_editable()
        res = super().write(vals)
        if "product_uom_qty" in vals:
            self._sync_stage_moves()
        return res

    @api.ondelete(at_uninstall=False)
    def _unlink_except_processed(self):
        self._check_editable()
        for line in self.filtered(
            lambda line: line.transfer_id.state in EDITABLE_STATES
        ):
            if line.qty_shipped or line.qty_received:
                raise UserError(
                    _(
                        "%(product)s has already been processed and cannot be "
                        "removed. Instead, create a return in your inventory.",
                        product=line.product_id.display_name,
                    )
                )

    def unlink(self):
        self._unlink_except_processed()
        to_cancel = self.env["stock.move"]
        for line in self.filtered(
            lambda line: line.transfer_id.state in EDITABLE_STATES
        ):
            to_cancel |= line.move_ids.filtered(
                lambda m: m.state not in ("done", "cancel")
            )
        to_cancel._action_cancel()
        return super().unlink()

    # === GETTERS ===

    def _get_stage_qty(self, stage, moves=None):
        """Quantity of `stage` already covered by moves, in the line UoM."""
        self.ensure_one()
        moves = self._get_stage_moves(stage) if moves is None else moves
        qty = 0.0
        for move in moves:
            move_qty = move.quantity if move.state == "done" else move.product_uom_qty
            qty += move.product_uom._compute_quantity(
                move_qty, self.product_uom, rounding_method="HALF-UP"
            )
        return qty

    def _get_stage_open_qty(self, stage):
        self.ensure_one()
        moves = self._get_stage_moves(stage).filtered(lambda m: m.state != "done")
        return self._get_stage_qty(stage, moves=moves)

    def _get_stage_done_qty(self, stage):
        self.ensure_one()
        moves = self._get_stage_moves(stage).filtered(lambda m: m.state == "done")
        return self._get_stage_qty(stage, moves=moves)

    def _get_stage_moves(self, stage):
        self.ensure_one()
        return self.move_ids.filtered(
            lambda m: m.picking_type_id.code == stage and m.state != "cancel"
        )

    def _get_stock_move_vals(
        self, picking_type, location, location_dest, group, qty=None
    ):
        self.ensure_one()
        transfer = self.transfer_id
        vals = {
            "name": self.product_id.name,
            "product_id": self.product_id.id,
            "product_uom": self.product_uom.id,
            "product_uom_qty": self.product_uom_qty if qty is None else qty,
            "picking_type_id": picking_type.id,
            "location_id": location.id,
            "location_dest_id": location_dest.id,
            "group_id": group.id,
            "origin": transfer.name,
            "company_id": transfer.company_id.id,
            "interwh_transfer_line_id": self.id,
        }
        if transfer.scheduled_date:
            vals["date"] = transfer.scheduled_date
        return vals

    # === BUSINESS METHODS ===

    def _sync_stage_moves(self):
        lines = self.filtered(lambda line: line.transfer_id.state in EDITABLE_STATES)
        moves = self.env["stock.move"]
        for transfer, transfer_lines in lines.grouped("transfer_id").items():
            moves |= transfer._sync_stage_moves(transfer_lines)
        return moves

    def _link_stage_moves(self):
        for line in self:
            out_moves = line._get_stage_moves("outgoing")
            if not out_moves:
                continue
            for move in line._get_stage_moves("incoming"):
                rounding = move.product_uom.rounding
                if move.state == "done" or move.move_orig_ids == out_moves:
                    continue
                if (
                    float_compare(
                        move.product_uom_qty, 0.0, precision_rounding=rounding
                    )
                    <= 0
                ):
                    continue
                move.move_orig_ids = [fields.Command.set(out_moves.ids)]
