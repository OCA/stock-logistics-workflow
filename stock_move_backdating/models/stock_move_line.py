# Copyright 2018 Alex Comba - Agile Business Group
# Copyright 2023 Simone Rubino - TAKOBI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import UserError


def check_date(record, date):
    now = fields.Datetime.now()
    if date and date > now:
        raise UserError(
            record.env._("You can not process an actual movement date in the future.")
        )


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    date_backdating = fields.Datetime(
        string="Actual Movement Date",
    )

    @api.onchange("date_backdating")
    def onchange_date_backdating(self):
        self.ensure_one()
        check_date(self, self.date_backdating)
