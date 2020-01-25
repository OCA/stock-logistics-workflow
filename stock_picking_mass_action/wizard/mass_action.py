# Copyright 2014 Camptocamp SA - Guewen Baconnier
# Copyright 2018 Tecnativa - Vicent Cubells
# Copyright 2019 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields
from odoo.models import TransientModel


class StockPickingMassAction(TransientModel):
    _name = "stock.picking.mass.action"
    _description = "Stock Picking Mass Action"

    @api.model
    def _default_check_availability(self):
        return self.env.context.get("check_availability", False)

    @api.model
    def _default_transfer(self):
        return self.env.context.get("transfer", False)

    def _default_picking_ids(self):
        return self.env["stock.picking"].browse(self.env.context.get("active_ids"))

    confirm = fields.Boolean(
        string="Mark as Todo",
        default=True,
        help="check this box if you want to mark as Todo the" " selected Pickings.",
    )
    check_availability = fields.Boolean(
        string="Check Availability",
        default=lambda self: self._default_check_availability(),
        help="check this box if you want to check the availability of"
        " the selected Pickings.",
    )
    transfer = fields.Boolean(
        string="Transfer",
        default=lambda self: self._default_transfer(),
        help="check this box if you want to transfer all the selected"
        " pickings.\n You'll not have the possibility to realize a"
        " partial transfer.\n If you want  to do that, please do it"
        " manually on the picking form.",
    )
    picking_ids = fields.Many2many(
        string="Pickings",
        comodel_name="stock.picking",
        default=lambda self: self._default_picking_ids(),
        help="",
    )

    def mass_action(self):
        self.ensure_one()

        # Get draft pickings and confirm them if asked
        if self.confirm:
            draft_picking_lst = self.picking_ids.filtered(
                lambda x: x.state == "draft"
            ).sorted(key=lambda r: r.scheduled_date)
            draft_picking_lst.action_confirm()

        # check availability if asked
        if self.check_availability:
            pickings_to_check = self.picking_ids.filtered(
                lambda x: x.state not in ["draft", "cancel", "done"]
            ).sorted(key=lambda r: r.scheduled_date)
            pickings_to_check.action_assign()

        # Get all pickings ready to transfer and transfer them if asked
        if self.transfer:
            assigned_picking_lst = self.picking_ids.filtered(
                lambda x: x.state == "assigned"
            ).sorted(key=lambda r: r.scheduled_date)
            quantities_done = sum(
                move_line.qty_done
                for move_line in assigned_picking_lst.mapped("move_line_ids").filtered(
                    lambda m: m.state not in ("done", "cancel")
                )
            )
            if not quantities_done:
                return assigned_picking_lst.action_immediate_transfer_wizard()
            if any([pick._check_backorder() for pick in assigned_picking_lst]):
                return assigned_picking_lst.action_generate_backorder_wizard()
            assigned_picking_lst.action_done()
