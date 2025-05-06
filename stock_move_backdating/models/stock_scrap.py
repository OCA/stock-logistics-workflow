# Copyright 2024 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from .stock_move_line import check_date


class StockScrap(models.Model):
    _inherit = "stock.scrap"

    date_backdating = fields.Datetime(
        string="Forced Effective Date",
        copy=False,
        help="The Actual Movement Date of the Operations "
        "only if they have all the same value.",
    )

    @api.onchange("date_backdating")
    def onchange_date_backdating(self):
        self.ensure_one()
        check_date(self.date_backdating)

    def _prepare_move_values(self):
        """Update backdating into stock move line"""
        self.ensure_one()
        move_dict = super()._prepare_move_values()
        move_dict["move_line_ids"][0][2]["date_backdating"] = self.date_backdating
        return move_dict
