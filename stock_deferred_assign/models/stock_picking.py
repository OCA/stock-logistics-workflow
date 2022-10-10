# Copyright 2021 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_assign(self):
        """ Override to filter pickings when the method is called by
            _action_launch_stock_rule (procurement_jit)
        """
        if not self.env.context.get("from_launch_stock_rule", False):
            return super().action_assign()
        # Exclude incoming pickings
        incoming_pickings = self.filtered(
            lambda p: p.picking_type_id.code == "incoming"
        )
        pickings = self.browse()
        for picking in self - incoming_pickings:
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
        pickings += incoming_pickings
        if pickings:
            return super(StockPicking, pickings).action_assign()
        return True
