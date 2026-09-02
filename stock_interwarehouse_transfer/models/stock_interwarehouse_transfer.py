# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero

STAGES = ("outgoing", "incoming")


class StockInterwarehouseTransfer(models.Model):
    _name = "stock.interwarehouse.transfer"
    _description = "Inter-Warehouse Transfer"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name desc"

    name = fields.Char(
        default="/",
        readonly=True,
        copy=False,
    )
    warehouse_from_id = fields.Many2one(
        "stock.warehouse",
        string="From Warehouse",
        required=True,
        check_company=True,
    )
    warehouse_to_id = fields.Many2one(
        "stock.warehouse",
        string="To Warehouse",
        required=True,
        check_company=True,
    )
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
    )
    location_id = fields.Many2one(
        "stock.location",
        string="From Location",
        compute="_compute_locations",
        store=True,
        precompute=True,
        readonly=False,
    )
    location_dest_id = fields.Many2one(
        "stock.location",
        string="To Location",
        compute="_compute_locations",
        store=True,
        precompute=True,
        readonly=False,
    )
    scheduled_date = fields.Datetime()
    line_ids = fields.One2many(
        "stock.interwarehouse.transfer.line",
        "transfer_id",
        string="Products",
    )
    picking_ids = fields.One2many(
        "stock.picking",
        "interwarehouse_transfer_id",
        string="Transfers",
        copy=False,
    )
    picking_count = fields.Integer(
        compute="_compute_picking_count",
        string="Transfer Count",
    )
    procurement_group_id = fields.Many2one(
        "procurement.group",
        string="Procurement Group",
        copy=False,
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("in_transit", "In Transit"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        compute="_compute_state",
        store=True,
        default="draft",
    )

    # === COMPUTE METHODS ===

    @api.depends("warehouse_from_id", "warehouse_to_id")
    def _compute_locations(self):
        for rec in self:
            if rec.warehouse_from_id:
                rec.location_id = rec.warehouse_from_id.lot_stock_id
            if rec.warehouse_to_id:
                rec.location_dest_id = rec.warehouse_to_id.lot_stock_id

    @api.depends("picking_ids")
    def _compute_picking_count(self):
        for rec in self:
            rec.picking_count = len(rec.picking_ids)

    @api.depends("picking_ids.state")
    def _compute_state(self):
        for rec in self:
            if not rec.picking_ids:
                rec.state = "draft"
                continue
            non_cancelled = rec.picking_ids.filtered(lambda p: p.state != "cancel")
            if not non_cancelled:
                rec.state = "cancelled"
                continue
            outgoing = non_cancelled.filtered(
                lambda p: p.picking_type_id.code == "outgoing"
            )
            incoming = non_cancelled.filtered(
                lambda p: p.picking_type_id.code == "incoming"
            )
            if incoming and all(p.state == "done" for p in incoming):
                rec.state = "done"
            elif outgoing and all(p.state == "done" for p in outgoing):
                rec.state = "in_transit"
            else:
                rec.state = "confirmed"

    # === CONSTRAINT METHODS ===

    @api.constrains("warehouse_from_id", "warehouse_to_id")
    def _check_same_company(self):
        for rec in self:
            if rec.warehouse_from_id.company_id != rec.warehouse_to_id.company_id:
                raise ValidationError(
                    _("Both warehouses must belong to the same company.")
                )
            if rec.warehouse_from_id == rec.warehouse_to_id:
                raise ValidationError(
                    _("Source and destination warehouse must be different.")
                )

    # === CRUD METHODS ===

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "/") == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "stock.interwarehouse.transfer"
                )
        return super().create(vals_list)

    # === ACTION METHODS ===

    def action_confirm(self):
        for rec in self:
            if not rec.line_ids:
                raise ValidationError(_("Cannot confirm a transfer without lines."))
            rec._ensure_transit_location()
            rec.warehouse_from_id._ensure_inter_wh_op_types()
            rec.warehouse_to_id._ensure_inter_wh_op_types()
            pickings = rec._sync_stage_moves().mapped("picking_id")
            rec.message_post(
                body=_(
                    "Transfer confirmed. OUT: %(out)s, IN: %(in_picking)s",
                    out=", ".join(
                        pickings.filtered(
                            lambda p: p.picking_type_id.code == "outgoing"
                        ).mapped("name")
                    ),
                    in_picking=", ".join(
                        pickings.filtered(
                            lambda p: p.picking_type_id.code == "incoming"
                        ).mapped("name")
                    ),
                )
            )

    def action_cancel(self):
        for rec in self:
            cancellable = rec.picking_ids.filtered(
                lambda p: p.state not in ("done", "cancel")
            )
            cancellable.action_cancel()

    def action_view_pickings(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "stock.picking",
            "view_mode": "tree,form",
            "domain": [("interwarehouse_transfer_id", "=", self.id)],
            "context": {"group_by": ["picking_type_id"]},
            "name": _("Transfers"),
        }

    # === GETTERS ===

    def _get_stage_qty_to_sync(self, stage, lines):
        """Return ``{line: qty}`` to add to `stage`, negative to remove.

        Resolved per stage, never once for both: the stages diverge as soon as
        one loses quantity the other keeps (a short validation without backorder).
        """
        self.ensure_one()
        lines_qty = {}
        for line in lines:
            qty = line.product_uom_qty - line._get_stage_qty(stage)
            if float_is_zero(qty, precision_rounding=line.product_uom.rounding):
                continue
            line._check_stage_decrease(stage, qty)
            lines_qty[line] = qty
        return lines_qty

    def _get_stage_config(self, stage):
        self.ensure_one()
        transit_loc = self._ensure_transit_location()
        if stage == "outgoing":
            return (
                self.warehouse_from_id.out_inter_wh_type_id,
                self.location_id,
                transit_loc,
            )
        return (
            self.warehouse_to_id.in_inter_wh_type_id,
            transit_loc,
            self.location_dest_id,
        )

    # === BUSINESS METHODS ===

    def _sync_stage_moves(self, lines=None):
        """Reconcile the moves of both stages with the demand of `lines`.

        Root of every move creation, first confirmation included -- with no move
        yet, the quantity to sync is simply the whole demand.
        """
        self.ensure_one()
        lines = self.line_ids if lines is None else lines
        moves = self.env["stock.move"]
        for stage in STAGES:
            moves |= self._create_stage_moves(
                stage, self._get_stage_qty_to_sync(stage, lines)
            )
        if not moves:
            return moves
        lines._link_stage_moves()
        return moves._action_confirm()

    def _create_stage_moves(self, stage, lines_qty):
        self.ensure_one()
        if not lines_qty:
            return self.env["stock.move"]
        group = self._ensure_procurement_group()
        picking_type, location, location_dest = self._get_stage_config(stage)
        return self.env["stock.move"].create(
            [
                line._get_stock_move_vals(
                    picking_type, location, location_dest, group, qty=qty
                )
                for line, qty in lines_qty.items()
            ]
        )

    def _ensure_procurement_group(self):
        self.ensure_one()
        if not self.procurement_group_id:
            self.procurement_group_id = self.env["procurement.group"].create(
                {"name": self.name}
            )
        return self.procurement_group_id

    def _ensure_transit_location(self):
        self.ensure_one()
        transit_loc = self.warehouse_from_id.company_id.internal_transit_location_id
        if not transit_loc:
            raise ValidationError(
                _(
                    "No internal transit location configured for company %(company)s.",
                    company=self.warehouse_from_id.company_id.name,
                )
            )
        return transit_loc
