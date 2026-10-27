# Copyright 2026 Jarsa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    next_picking_id = fields.Many2one(
        comodel_name="stock.picking",
        string="Next Operation",
        compute="_compute_next_picking_id",
        store=True,
        help="First chained transfer that follows this one, e.g. the pack "
        "of what this transfer picks.",
    )
    next_picking_user_id = fields.Many2one(
        comodel_name="res.users",
        string="Next Operation Responsible",
        compute="_compute_next_picking_user_id",
        inverse="_inverse_next_picking_user_id",
        store=True,
        domain=[("share", "=", False)],
        help="Responsible of the next operation, e.g. who packs what this "
        "transfer picks. Changing it changes the responsible of that "
        "transfer.",
    )

    picking_progress = fields.Char(
        string="Progress",
        compute="_compute_picking_progress",
        help="Picked lines over the lines of the transfer.",
    )
    is_in_progress = fields.Boolean(
        string="In Progress",
        compute="_compute_picking_progress",
        search="_search_is_in_progress",
        help="Ready transfer where the operator already picked some lines "
        "(e.g. scanned them in the barcode app) but did not validate yet.",
    )

    @api.depends("state", "move_ids.picked")
    def _compute_picking_progress(self):
        for picking in self:
            moves = picking.move_ids.filtered(lambda m: m.state not in ("cancel",))
            picked = len(moves.filtered("picked"))
            picking.picking_progress = f"{picked}/{len(moves)}" if moves else ""
            picking.is_in_progress = picking.state == "assigned" and bool(picked)

    def _search_is_in_progress(self, operator, value):
        if operator not in ("=", "!="):
            raise NotImplementedError
        domain = [("state", "=", "assigned"), ("move_ids.picked", "=", True)]
        return domain if (operator == "=") == bool(value) else ["!", *domain]

    @api.depends("move_ids.move_dest_ids.picking_id.state")
    def _compute_next_picking_id(self):
        for picking in self:
            picking.next_picking_id = (
                picking.move_ids.move_dest_ids.picking_id.filtered(
                    lambda p: p.state not in ("done", "cancel")
                )[:1]
            )

    @api.depends("next_picking_id.user_id")
    def _compute_next_picking_user_id(self):
        for picking in self:
            picking.next_picking_user_id = picking.next_picking_id.user_id

    def _inverse_next_picking_user_id(self):
        for picking in self.filtered("next_picking_id"):
            picking.next_picking_id.user_id = picking.next_picking_user_id

    def action_confirm(self):
        res = super().action_confirm()
        # Chained transfer confirmed after the previous one already got its
        # responsible (e.g. created by hand): assign it now.
        for picking in self.filtered(
            lambda p: p.picking_type_id.responsible_assign_mode == "previous"
        ):
            previous = picking.move_ids.move_orig_ids.picking_id.filtered(
                lambda p: p.user_id
                and p.picking_type_id.responsible_assign_mode != "manual"
                and p.user_id in p.picking_type_id._get_assignable_users()
            )
            previous[:1]._auto_assign_chained_responsible()
        return res

    def action_auto_assign_responsible(self):
        """Reassign, skipping the transfers somebody already started."""
        in_progress = self.filtered("is_in_progress")
        if in_progress and in_progress == self:
            raise UserError(
                self.env._(
                    "%(pickings)s: already in progress, change the responsible by "
                    "hand if you really want to take it away from %(users)s.",
                    pickings=", ".join(in_progress.mapped("name")),
                    users=", ".join(in_progress.user_id.mapped("name")),
                )
            )
        (self - in_progress)._auto_assign_responsible(force=True)

    def _auto_assign_responsible(self, force=False):
        """Assign the least loaded user of the operation type pool. Returns
        whether every transfer got a responsible.

        Without ``force`` a responsible already in the pool is kept, so a
        manual choice of the warehouse manager is respected and repeated
        reservations do not reshuffle the work. A responsible outside the
        pool (the salesperson that confirmed the order, the scheduler bot)
        is always replaced. When the pool is at its maximum of pending
        transfers the transfer is left unassigned, queued for later.
        """
        assigned = True
        for picking in self:
            picking_type = picking.picking_type_id
            users = picking_type._get_assignable_users()
            if not users:
                continue
            if not force and picking.user_id in users:
                continue
            # sudo: the reservation may run as a salesperson or the scheduler,
            # which may not see or write every pending transfer.
            picking_sudo = picking.sudo()
            user = picking_type.sudo()._get_least_loaded_user(users)
            if not user:
                picking_sudo.user_id = False
                assigned = False
                continue
            picking_sudo.user_id = user
            picking_sudo._auto_assign_chained_responsible(force=force)
        return assigned

    def _action_done(self):
        res = super()._action_done()
        # a finished transfer frees its user: hand out the next queued one
        self.picking_type_id.sudo()._assign_queued_pickings()
        return res

    def action_cancel(self):
        res = super().action_cancel()
        self.picking_type_id.sudo()._assign_queued_pickings()
        return res

    def _auto_assign_chained_responsible(self, force=False):
        for picking in self:
            next_pickings = picking.move_ids.move_dest_ids.picking_id.filtered(
                lambda p: p.state not in ("done", "cancel")
                and p.picking_type_id.responsible_assign_mode == "previous"
            )
            for next_picking in next_pickings:
                if next_picking.picking_type_id.responsible_assign_same_user:
                    next_picking.user_id = picking.user_id
                    next_picking._auto_assign_chained_responsible(force=force)
                else:
                    next_picking._auto_assign_responsible(force=force)
