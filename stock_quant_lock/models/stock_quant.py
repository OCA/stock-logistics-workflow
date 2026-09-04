# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero


class StockQuant(models.Model):
    _inherit = "stock.quant"

    lock_move_count = fields.Integer(
        string="Lock Moves",
        compute="_compute_lock_move_count",
    )
    is_locked_by_picking = fields.Boolean(
        string="Locked by picking",
        compute="_compute_is_locked_by_picking",
        store=True,
        index=True,
    )
    lock_move_ids = fields.One2many(
        comodel_name="stock.move",
        inverse_name="quant_lock_quant_id",
        string="Lock Moves",
        readonly=True,
    )

    def _get_lock_move_domain(self, active_only=False):
        if self.ids:
            domain = [("quant_lock_quant_id", "in", self.ids)]
        else:
            domain = [("quant_lock_quant_id", "!=", False)]
        if active_only:
            domain.append(("state", "=", "assigned"))
        return domain

    def _get_lock_move_counts(self, active_only=False):
        if not self:
            return {}
        groups = self.env["stock.move"].read_group(
            self._get_lock_move_domain(active_only=active_only),
            ["quant_lock_quant_id"],
            ["quant_lock_quant_id"],
        )
        move_counts = {}
        for group in groups:
            quant_data = group.get("quant_lock_quant_id")
            if not quant_data:
                continue
            move_counts[quant_data[0]] = group.get(
                "quant_lock_quant_id_count", group.get("__count", 0)
            )
        return move_counts

    @api.depends("lock_move_ids", "lock_move_ids.state")
    def _compute_lock_move_count(self):
        move_counts = self._get_lock_move_counts()
        for quant in self:
            quant.lock_move_count = move_counts.get(quant.id, 0)

    @api.depends("lock_move_ids", "lock_move_ids.state")
    def _compute_is_locked_by_picking(self):
        active_move_counts = self._get_lock_move_counts(active_only=True)
        for quant in self:
            quant.is_locked_by_picking = active_move_counts.get(quant.id, 0) > 0

    def _gather(
        self,
        product_id,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=False,
    ):
        # If a specific quant is forced in the context and strict mode is enabled,
        # only return that quant if it matches the requested characteristics.
        force_quant_id = self.env.context.get("force_quant_lock_quant_id")
        if force_quant_id and strict:
            quant = self.browse(force_quant_id).exists()
            if (
                quant
                and quant.product_id.id == product_id.id
                and quant.location_id.id == location_id.id
                and quant.lot_id == lot_id
                and quant.package_id == package_id
                and quant.owner_id == owner_id
            ):
                return quant
        return super()._gather(
            product_id,
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
        )

    def action_open_lock_wizard(self):
        return {
            "name": _("Lock Quants"),
            "type": "ir.actions.act_window",
            "res_model": "stock.quant.lock.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "active_model": "stock.quant",
                "active_ids": self.ids,
            },
        }

    def action_view_lock_moves(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("stock.stock_move_action")
        action["domain"] = [("quant_lock_quant_id", "=", self.id)]
        action["context"] = {"search_default_done": 0}
        return action

    def action_unlock_quant(self):
        done_moves = self.env["stock.move"].search(
            self._get_lock_move_domain(active_only=False) + [("state", "=", "done")],
            limit=1,
        )
        if done_moves:
            raise UserError(
                _(
                    "You cannot unlock quant '%(quant)s' because lock move '%(move)s' is done.",
                    quant=done_moves.quant_lock_quant_id.display_name,
                    move=done_moves.display_name,
                )
            )

        active_moves = self.env["stock.move"].search(
            self._get_lock_move_domain(active_only=True)
        )
        if active_moves:
            active_moves._action_cancel()
        return True

    def _check_is_lock_with_picking_type_allowed(self, picking_type, raise_error=True):
        self.ensure_one()
        if self.is_locked_by_picking:
            if raise_error:
                raise UserError(
                    _(
                        "Quant '%(quant)s' is already locked.",
                        quant=self.display_name,
                    )
                )
            return False
        if not picking_type.allow_quant_lock:
            if raise_error:
                raise UserError(
                    _(
                        "Operation type '%(op)s' cannot be used for quant lock.",
                        op=picking_type.display_name,
                    )
                )
            return False

    def _lock_with_picking_type(self, picking_type):
        """Lock the quant using the specified picking type.

        This will create a stock move of the specified picking type
        and reserve the remaining available quantity for the quant.
        """
        self._check_is_lock_with_picking_type_allowed(picking_type, raise_error=True)
        lock_move_vals = self._prepare_lock_move_vals(picking_type)
        qty_to_lock = lock_move_vals["product_uom_qty"]
        move = self.env["stock.move"].create(lock_move_vals)
        move._action_confirm()
        picking = move.picking_id
        if not picking:
            raise UserError(
                _("Unable to create lock picking for quant '%s'.") % self.display_name
            )
        move._action_assign()

        if (
            float_compare(
                move.reserved_availability,
                qty_to_lock,
                precision_rounding=self.product_uom_id.rounding,
            )
            < 0
        ):
            picking.action_cancel()
            raise UserError(
                _(
                    "Unable to reserve full available quantity for quant '%(quant)s'. "
                    "Expected %(expected)s %(uom)s, reserved %(reserved)s %(uom)s.",
                    expected=qty_to_lock,
                    reserved=move.reserved_availability,
                    uom=self.product_uom_id.display_name,
                )
            )

        return picking

    def _prepare_lock_move_vals(self, picking_type):
        self.ensure_one()
        qty_to_lock = self.available_quantity
        if float_is_zero(qty_to_lock, precision_rounding=self.product_uom_id.rounding):
            raise UserError(
                _("No available quantity to lock for quant '%s'.") % self.display_name
            )
        location_dest = (
            picking_type.default_location_dest_id
            or picking_type.default_location_src_id
        )
        if not location_dest:
            raise UserError(
                _(
                    "Operation type '%(op)s' must define at least one default "
                    "location.",
                    op=picking_type.display_name,
                )
            )
        return {
            "name": _("Quant lock for %s") % self.product_id.display_name,
            "product_id": self.product_id.id,
            "product_uom": self.product_uom_id.id,
            "product_uom_qty": qty_to_lock,
            "location_id": self.location_id.id,
            "location_dest_id": location_dest.id,
            "picking_type_id": picking_type.id,
            "quant_lock_quant_id": self.id,
            "company_id": self.company_id.id,
            "origin": _("Quant lock: %s") % self.display_name,
        }
