# Copyright 2018 Alex Comba - Agile Business Group
# Copyright 2023 Simone Rubino - TAKOBI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

from ..utils import check_date


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    date_backdating = fields.Datetime(
        string="Actual Movement Date",
    )

    @api.onchange(
        "date_backdating",
    )
    def onchange_date_backdating(self):
        self.ensure_one()
        check_date(self.date_backdating)
