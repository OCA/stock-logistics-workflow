# Copyright 2023 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Picking(models.Model):
    _inherit = "stock.picking"

    force_date = fields.Datetime(
        copy=False,
        help="Force the moves to a given date",
    )

    def _action_done(self):
        res = super()._action_done()
        for rec in self.filtered("force_date"):
            rec.write({"date_done": rec.force_date})
        return res
