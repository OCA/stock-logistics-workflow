# Copyright 2021 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields, models


class PickingType(models.Model):
    _inherit = "stock.picking.type"

    reservation_method = fields.Selection(
        [
            ("at_confirm", "At Confirmation"),
            ("manual", "Manually"),
            ("by_date", "Before scheduled date"),
        ],
        "Reservation Method",
        required=True,
        default="at_confirm",
        help="How products in transfers of this operation type should be reserved.",
    )
    reservation_days_before = fields.Integer(
        "Days",
        help="Maximum number of days before scheduled date that products "
        "should be reserved.",
    )


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_assign(self):
        """ Override to filter pickings when the method is called by
            _action_launch_stock_rule (procurement_jit)
        """
        if not self.env.context.get("from_launch_stock_rule", False):
            return super().action_assign()
        pickings = self.browse()
        for picking in self:
            method = picking.picking_type_id.reservation_method
            days_before = picking.picking_type_id.reservation_days_before
            reservation_date = fields.Date.to_date(picking.scheduled_date) - timedelta(
                days=days_before
            )
            if method == "at_confirm" or (
                method == "by_date" and reservation_date <= fields.Date.today()
            ):
                pickings |= picking
        # Avoid raise if 'Nothing to check the availability for'
        if pickings:
            return super(StockPicking, pickings).action_assign()
        else:
            return True
