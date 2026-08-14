# Copyright 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, exceptions, fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    locked = fields.Boolean(
        compute="_compute_locked",
        inverse="_inverse_locked",
        store=True,
        copy=False,
    )

    stage_id = fields.Many2one(
        "stock.lot.stage",
        string="Stage",
        tracking=True,
        default=lambda self: self._default_stage_id(),
        group_expand="_read_group_stage_ids",
        copy=False,
        index=True,
    )
    partial_approved_qty = fields.Float(
        string="Partial Approved Quantity",
        help="Maximum quantity allowed in locations that don't allow locked lots."
        "Leave zero to approve the full quantity.",
        tracking=True,
        copy=False,
    )
    usable_location_qty = fields.Float(
        compute="_compute_usable_location_qty",
        help="Total quantity in locations where locked lots are not allowed.",
    )
    # For improved auditability, the last unlocker and time are stored
    last_unlocked_by = fields.Many2one(
        "res.users",
        readonly=True,
        help="User who last unlocked this lot",
        copy=False,
    )
    last_unlocked_at = fields.Datetime(
        readonly=True,
        help="Date and time when this lot was last unlocked",
        copy=False,
    )

    @api.model
    def _default_stage_id(self):
        return self.env["stock.lot.stage"].search([], limit=1)

    @api.depends("stage_id.locked")
    def _compute_locked(self):
        for lot in self:
            old_locked = lot.locked
            lot.locked = lot.stage_id.locked
            # Track unlock operations when computed value changes from True to False
            if old_locked and not lot.locked:
                lot.last_unlocked_by = lot.env.uid
                lot.last_unlocked_at = fields.Datetime.now()

    def _inverse_locked(self):
        for lot in self:
            stage = lot._get_stage_for_locked(lot.locked)
            if stage and stage != lot.stage_id:
                lot.stage_id = stage

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return stages.search([], order=order)

    @api.depends("quant_ids.quantity", "quant_ids.location_id")
    def _compute_usable_location_qty(self):
        for lot in self:
            lot.usable_location_qty = sum(
                lot.quant_ids.filtered(
                    lambda q: not q.location_id.allow_locked
                    and q.location_id.usage == "internal"
                ).mapped("quantity")
            )

    @api.constrains("stage_id")
    def _check_stage_change(self):
        stage_changed = any(lot.stage_id != lot._origin.stage_id for lot in self)
        can_lock_lot = self.user_has_groups("stock_lock_lot.group_lock_lot")
        if stage_changed and not can_lock_lot:
            raise exceptions.AccessError(_("You are not allowed to change lot stages."))

    @api.constrains("stage_id", "partial_approved_qty")
    def _check_partial_qty_stage_compatibility(self):
        """Check that partial approved quantity is compatible with the current stage."""
        for lot in self.filtered("stage_id"):
            # Partial quantities are not allowed in stages that require full approval
            if lot.stage_id.locked:
                continue
            if lot.stage_id.approve_full_qty and lot.partial_approved_qty > 0:
                raise exceptions.ValidationError(
                    _(
                        "Partial approved quantity cannot be set "
                        "on lots in stages that require full approval. "
                        "Lot '%(lot)s' has a partial approved quantity "
                        "but is in stage '%(stage)s' which requires full approval. "
                        "Either clear the partial approved quantity "
                        "or move the lot to a stage that allows partial approval.",
                        lot=lot.name,
                        stage=lot.stage_id.name,
                    )
                )

            # Stages that allow partial approval must have partial qty set
            if not lot.stage_id.approve_full_qty and lot.partial_approved_qty == 0:
                raise exceptions.ValidationError(
                    _(
                        "Lots in stage '%(stage)s' must have "
                        "a partial approved quantity set. "
                        "Please set a partial approved quantity "
                        "or move the lot to a different stage.",
                        stage=lot.stage_id.name,
                    )
                )

    @api.constrains("partial_approved_qty")
    def _check_partial_approved_qty(self):
        is_partial = any(self.mapped("partial_approved_qty"))
        if is_partial and not self.user_has_groups("stock_lock_lot.group_lock_lot"):
            raise exceptions.AccessError(
                _("You are not allowed to change the partial approved quantity.")
            )

        # Validate that partial approved quantity is not negative
        if any(lot.partial_approved_qty < 0 for lot in self):
            raise exceptions.ValidationError(
                _("Partial approved quantity cannot be negative.")
            )

        # Run quant validation to ensure current quantities don't exceed the new limit
        lots_to_check = self.filtered("partial_approved_qty")
        lots_to_check.quant_ids._check_partial_approved_qty()

    def _get_stage_for_locked(self, locked):
        """Return the first stage matching the locked value."""
        domain = [("locked", "=", locked)]
        domain += [("approve_full_qty", "=", True)] if not locked else []
        return self.env["stock.lot.stage"].search(domain, limit=1)

    @api.model_create_multi
    def create(self, vals_list):
        lots = super().create(vals_list)
        for lot in lots:
            if not lot.stage_id or lot.stage_id == self._default_stage_id():
                stage = lot._get_stage_for_locked(lot.locked)
                if stage and stage != lot.stage_id:
                    lot.stage_id = stage
        return lots
