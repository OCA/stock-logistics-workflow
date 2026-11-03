# Copyright 2026 Jarsa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models

PENDING_STATES = ("confirmed", "waiting", "assigned")


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    responsible_user_ids = fields.Many2many(
        comodel_name="res.users",
        relation="stock_picking_type_responsible_user_rel",
        string="Responsible Pool",
        domain=[("share", "=", False)],
        help="Internal users that receive the transfers of this operation "
        "type automatically, e.g. warehouse operators restricted to their "
        "operation types. The transfer goes to the user with the lowest "
        "pending workload.",
    )
    responsible_assign_mode = fields.Selection(
        selection=[
            ("manual", "Manual"),
            ("ready", "When the transfer is ready"),
            ("previous", "Together with the previous operation"),
        ],
        string="Responsible Assignment",
        default="manual",
        required=True,
        help="Manual: nothing is assigned automatically.\n"
        "When the transfer is ready: assign the responsible as soon as the "
        "transfer is reserved.\n"
        "Together with the previous operation: assign the responsible when "
        "the chained previous transfer (e.g. pick before pack) gets its own "
        "responsible, so both users are known from the start.",
    )
    responsible_assign_same_user = fields.Boolean(
        string="Same Responsible as Previous Operation",
        help="Copy the responsible of the previous transfer instead of "
        "balancing the workload within the pool of this operation type.",
    )
    responsible_assign_max_pending = fields.Integer(
        string="Max Pending Transfers per User",
        default=0,
        help="Transfers a user can have pending at the same time. Beyond it "
        "the transfer waits unassigned and is handed out when the user "
        "finishes one, so the work flows as a queue. 0 means no limit.",
    )
    responsible_assign_load = fields.Selection(
        selection=[
            ("moves", "Number of lines"),
            ("quantity", "Quantity"),
            ("pickings", "Number of transfers"),
        ],
        string="Workload Measure",
        default="moves",
        required=True,
        help="What is summed over the pending transfers of each user to pick "
        "the least loaded one.",
    )

    def _get_assignable_users(self):
        self.ensure_one()
        return self.responsible_user_ids.filtered(
            lambda u: u.active and u.picking_assign_available
        )

    def _get_picking_load(self, picking):
        if self.responsible_assign_load == "quantity":
            return sum(picking.move_ids.mapped("product_uom_qty"))
        if self.responsible_assign_load == "pickings":
            return 1
        return len(picking.move_ids)

    def _get_least_loaded_user(self, users):
        """Return the user of ``users`` with the lowest pending workload on
        this operation type, or an empty recordset when every user already
        has the maximum of pending transfers. Ties are broken by the number
        of pending transfers and then by user id."""
        self.ensure_one()
        load = dict.fromkeys(users, 0.0)
        count = dict.fromkeys(users, 0)
        pending = self.env["stock.picking"].search(
            [
                ("picking_type_id", "=", self.id),
                ("user_id", "in", users.ids),
                ("state", "in", PENDING_STATES),
            ]
        )
        for picking in pending:
            load[picking.user_id] += self._get_picking_load(picking)
            count[picking.user_id] += 1
        if self.responsible_assign_max_pending:
            users = users.filtered(
                lambda u: count[u] < self.responsible_assign_max_pending
            )
        if not users:
            return self.env["res.users"]
        return min(users, key=lambda u: (load[u], count[u], u.id))

    def _assign_queued_pickings(self):
        """Hand out the ready transfers waiting for a responsible, most
        urgent first, until every user of the pool is at its maximum."""
        for picking_type in self.filtered(
            lambda t: t.responsible_assign_mode == "ready"
            and t.responsible_assign_max_pending
        ):
            users = picking_type._get_assignable_users()
            queued = self.env["stock.picking"].search(
                [
                    ("picking_type_id", "=", picking_type.id),
                    ("state", "=", "assigned"),
                    ("user_id", "not in", users.ids),
                ],
                order="priority desc, scheduled_date asc, id asc",
            )
            for picking in queued:
                if not picking._auto_assign_responsible():
                    break
