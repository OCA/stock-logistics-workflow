# Copyright 2018 Alex Comba - Agile Business Group
# Copyright 2023 Simone Rubino - TAKOBI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from ..models.stock_move_line import check_date


class FillDateBackdating(models.TransientModel):
    _name = "fill.date.backdating"
    _description = "Fill Actual Movement Date of all operations"

    date_backdating = fields.Datetime(
        string="Actual Movement Date",
    )

    @api.constrains(
        "date_backdating",
    )
    def constrain_date_backdating(self):
        try:
            check_date(self.date_backdating)
        except UserError as ue:
            raise ValidationError(ue.args[0]) from ue

    def fill_date_backdating(self):
        """Fill the Actual Movement Date on all pack operations."""
        self.ensure_one()
        picking_id = self.env.context["active_id"]
        picking = self.env["stock.picking"].browse(picking_id)
        picking.move_line_ids.update(
            {
                "date_backdating": self.date_backdating,
            }
        )
        return {
            "type": "ir.actions.act_window_close",
        }
