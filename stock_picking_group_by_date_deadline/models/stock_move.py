# Copyright 2023 Foodles (http://www.foodles.co).
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import timedelta

from odoo import api, fields, models
from odoo.osv import expression


class DeadlineDate:
    """purpose of this class is to wrap datetime
    in the id attribute as keys are expected in
    id attribute
    """

    id = False

    def __init__(self, dt):
        self.id = dt


class StockMove(models.Model):
    _inherit = "stock.move"

    date_deadline = fields.Datetime(inverse="_inverse_date_deadline")

    def _key_assign_picking(self):
        keys = super()._key_assign_picking()
        return keys + (DeadlineDate(self.date_deadline),)

    def _search_picking_for_assignation_domain(self):
        domain = super()._search_picking_for_assignation_domain()
        return expression.AND([domain, [("date_deadline", "=", self.date_deadline)]])

    def _inverse_date_deadline(self):
        if getattr(super(), "_inverse_date_deadline", None):
            super()._inverse_date_deadline()
        for move in self:
            move.date_deadline = self._round_date_deadline(move.date_deadline)

    @api.model
    def _round_date_deadline(self, deadline):
        """compute deadline date according given time and rounding time threshold
        set in hours
        """
        if not deadline:
            return deadline
        date_delta = timedelta(
            hours=float(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param(
                    "stock_picking_group_by_date_deadline.deadline_date_rounding_threshold",
                    default=24,
                )
            )
        )
        round_to = date_delta.total_seconds()
        seconds = (deadline - deadline.min).seconds
        rounding = seconds // round_to * round_to
        return deadline + timedelta(0, rounding - seconds, -deadline.microsecond)
