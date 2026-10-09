# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import clean_context
from odoo.tools.float_utils import float_compare, float_is_zero


class StockQuant(models.Model):
    _inherit = "stock.quant"

    lock_move_count = fields.Integer(
        compute="_compute_lock_move_count",
    )
    is_locked_by_picking = fields.Boolean(
        string="Locked by issue",
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
        if not self:
            return
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

    def _check_is_lock_with_route_allowed(self, route, raise_error=True):
        self.ensure_one()
        if not route.allow_quant_lock:
            if raise_error:
                raise UserError(
                    _(
                        "Route '%(route)s' cannot be used for quant lock.",
                        route=route.display_name,
                    )
                )
            return False
        if not self._get_lock_rule(route):
            if raise_error:
                raise UserError(
                    _(
                        "Route '%(route)s' has no pull rule from a location "
                        "containing '%(location)s' to lock quant '%(quant)s'.",
                        route=route.display_name,
                        location=self.location_id.display_name,
                        quant=self.display_name,
                    )
                )
            return False
        # A quant already locked can only be locked again for the same
        # purpose: the new lock move reserves the quantity released since then.
        picking_type = self._get_lock_rule(route).picking_type_id
        other_lock_moves = self.lock_move_ids.filtered(
            lambda m: m.state == "assigned" and m.picking_type_id != picking_type
        )
        if other_lock_moves:
            if raise_error:
                raise UserError(
                    _(
                        "Quant '%(quant)s' is already locked by '%(op)s'.",
                        quant=self.display_name,
                        op=other_lock_moves[0].picking_type_id.display_name,
                    )
                )
            return False
        return True

    def _get_lock_rule_domain(self, route):
        self.ensure_one()
        return [
            ("route_id", "in", route.ids),
            ("action", "in", ("pull", "pull_push")),
            ("procure_method", "=", "make_to_stock"),
            ("location_src_id", "parent_of", self.location_id.id),
            ("company_id", "in", (False, self.company_id.id)),
        ]

    def _get_lock_rule(self, route):
        """Return the rule of the route used to lock the quant.

        It is the pull rule whose source location is the closest parent of the
        quant location.
        """
        self.ensure_one()
        rules = self.env["stock.rule"].search(
            self._get_lock_rule_domain(route), order="route_sequence, sequence"
        )
        if not rules:
            return rules
        # we use the rule whose source location is the closest parent of the quant location
        # if there are multiple rules with the same source location,
        # we preserve the order of the rules as defined in the route (route_sequence, sequence)
        return max(
            rules,
            key=lambda rule: (
                len(rule.location_src_id.parent_path),
                -rules.ids.index(rule.id),
            ),
        )

    def _lock_with_route(self, route):
        """Lock the quant using the specified route.

        This will run a procurement on the lock rule of the route to create
        a stock move reserving the remaining available quantity of the quant.
        """
        self._check_is_lock_with_route_allowed(route, raise_error=True)
        # Drop default_* keys from the context (e.g. default_picking_id) so the
        # lock move is assigned to a picking of the operation type of the rule.
        # The context must be replaced, not updated, to remove these keys.
        ctx = clean_context(self.env.context)
        quant = self.with_context(ctx)  # pylint: disable=W8121
        procurement = quant._prepare_lock_procurement(route)
        qty_to_lock = procurement.product_qty
        # The quant may already be locked: only consider the lock move created
        # by this procurement.
        existing_moves = self.lock_move_ids
        quant.env["procurement.group"].run([procurement])
        move = self.env["stock.move"].search(
            [
                ("quant_lock_quant_id", "=", self.id),
                ("id", "not in", existing_moves.ids),
                ("state", "not in", ("done", "cancel")),
            ]
        )
        picking = move.picking_id
        if len(move) != 1 or not picking:
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
            # Only cancel the lock move: the picking may be shared with the
            # lock moves of other quants.
            move._action_cancel()
            raise UserError(
                _(
                    "Unable to reserve full available quantity for quant '%(quant)s'. "
                    "Expected %(expected)s %(uom)s, reserved %(reserved)s %(uom)s.",
                    quant=self.display_name,
                    expected=qty_to_lock,
                    reserved=move.reserved_availability,
                    uom=self.product_uom_id.display_name,
                )
            )

        return picking

    def _prepare_lock_procurement_values(self, route, rule):
        self.ensure_one()
        return {
            "route_ids": route,
            "warehouse_id": rule.warehouse_id or self.warehouse_id,
            "company_id": self.company_id,
            "quant_lock_quant_id": self,
        }

    def _prepare_lock_procurement(self, route):
        self.ensure_one()
        qty_to_lock = self.available_quantity
        if float_is_zero(qty_to_lock, precision_rounding=self.product_uom_id.rounding):
            raise UserError(
                _("No available quantity to lock for quant '%s'.") % self.display_name
            )
        rule = self._get_lock_rule(route)
        return self.env["procurement.group"].Procurement(
            self.product_id,
            qty_to_lock,
            self.product_uom_id,
            rule.location_dest_id,
            _("Quant lock for %s") % self.product_id.display_name,
            _("Quant lock: %s") % self.display_name,
            self.company_id,
            self._prepare_lock_procurement_values(route, rule),
        )
