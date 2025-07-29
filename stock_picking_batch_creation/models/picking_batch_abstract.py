# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import threading

from odoo import api, fields, models


class MakePickingBatchAbstract(models.AbstractModel):
    _name = "make.picking.batch.abstract"
    _description = "Make a batch picking wizard - Abstract"

    picking_type_ids = fields.Many2many(
        comodel_name="stock.picking.type",
        string="Default operation types",
        help="Default list of eligible operation types when creating a batch transfer",
    )
    stock_device_type_ids = fields.Many2many(
        comodel_name="stock.device.type",
        string="Default device types",
        help="Default list of eligible device types when creating a batch transfer",
    )
    user_id = fields.Many2one(
        "res.users", string="Responsible", default=lambda self: self.env.user
    )
    maximum_number_of_preparation_lines = fields.Integer(
        default=20,
        string="Maximum number of preparation lines for the batch",
        required=True,
    )
    group_pickings_by_partner = fields.Boolean(
        default=False,
        string="Group pickings by partner",
        help="All the pickings related to one partner will be put into the same bins",
    )
    restrict_to_same_priority = fields.Boolean(
        default=False,
        string="Restrict to the same priority",
        help="Only the pickings with the same priority will be selected "
        "for this batch.",
    )
    restrict_to_same_partner = fields.Boolean(
        default=False,
        string="Restrict to the same partner",
        help="Only the pickings with the same partner will be selected for this batch.",
    )
    picking_locking_mode = fields.Selection(
        selection=[
            ("sql_for_update_skip_locked", "SQL FOR UPDATE SKIP LOCKED"),
        ],
        default=lambda self: self._get_default_picking_locking_mode(),
        string="Picking locking mode",
        help="Define the way the system will search and lock the pickings. "
        "In the same time, picking already locked by another transaction will "
        "be skipped. This should reduce the risk of deadlocks if 2 users "
        "try to create a batch at the same time.",
    )
    add_picking_list_in_error = fields.Boolean(
        default=False,
        string="Add all the names of the pickings in error message",
        help="If not suitable device is provided for the pickings candidates, "
        "the error message will contain the list of the pickings names. In some"
        "cases, this list can be very long. That's why this option is unchecked"
        "by default.",
    )

    no_line_limit_if_no_candidate = fields.Boolean(
        default=True,
        string="No line limit if no candidate",
        help="If checked, the maximum number of lines will not be applied if there is "
        "no candidate to add to the batch with a number of lines less than the maximum "
        "number of lines. This option is useful if you want relax the maximum number "
        "of lines to allow to create a batch even if there is no candidate to add to "
        "the batch at first. This will avoid to manually create a batch with a single "
        "picking for the sole case where a device is suitable for the picking but the "
        "picking has more lines than the maximum number of lines.",
    )

    @api.model
    def _get_default_picking_locking_mode(self):
        # in test mode we don't use a locking mode by default to avoid
        # to collide with the test transaction
        if self.env.registry.in_test_mode() or getattr(
            threading.current_thread(), "testing", False
        ):
            return None
        return "sql_for_update_skip_locked"
