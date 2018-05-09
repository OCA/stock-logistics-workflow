# -*- coding: utf-8 -*-
# Copyright 2018 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


def check_date(date):
    now = fields.Datetime.now()
    if date > now:
        raise UserError(
            _("You can not process an actual "
              "movement date in the future."))


class PackOperation(models.Model):
    _inherit = "stock.pack.operation"

    date_backdating = fields.Datetime(string='Actual Movement Date')

    @api.onchange('date_backdating')
    def onchange_date_backdating(self):
        check_date(self.date_backdating)
