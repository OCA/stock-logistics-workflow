# Copyright 2018 Alex Comba - Agile Business Group
# Copyright 2023 Simone Rubino - TAKOBI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    date_backdating = fields.Datetime(
        string="Forced Effective Date",
        help="The Actual Movement Date of the Operations "
        "only if they have all the same value.",
        compute="_compute_date_backdating",
        store=True,
    )

    @api.depends("move_line_ids.date_backdating")
    def _compute_date_backdating(self):
        for picking in self:
            move_lines = picking.move_line_ids
            move_lines_back_dates = move_lines.mapped("date_backdating")
            move_lines_back_date = set(move_lines_back_dates)
            if len(move_lines_back_date) == 1:
                date_backdating = move_lines_back_date.pop()
            else:
                date_backdating = False
            picking.date_backdating = date_backdating

    def _backdating_update_picking_date(self):
        """Set date_done as the youngest date among the done moves."""
        self.ensure_one()
        moves = self.move_ids
        done_moves = moves.filtered(lambda m: m.state == "done")
        dates = done_moves.mapped("date")
        if dates:
            self.date_done = max(dates)
        return True

    def _backdating_update_stock_valuation_layers_date(self):
        """Set date on linked stock.valuation.layer same as date on stock.move."""
        self.ensure_one()
        stock_moves = self.move_ids
        stock_moves._backdating_stock_valuation_layers()
        return True

    def _action_done(self):
        result = super()._action_done()
        pickings_backdate = self.filtered_domain(
            [
                "|",
                ("date_backdating", "!=", False),
                ("move_ids.move_line_ids.date_backdating", "!=", False),
            ]
        )
        for picking in pickings_backdate:
            picking._backdating_update_picking_date()
            picking._backdating_update_stock_valuation_layers_date()
        return result
