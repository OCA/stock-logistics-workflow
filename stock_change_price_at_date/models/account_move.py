# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMove(models.Model):

    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        """
        Assuming there is no hook to prevent using context
        :return:
        """
        move_date = self.env.context.get('move_date', False)
        if 'date' not in vals and move_date:
            vals.update({
                'date': move_date,
            })
        return super(AccountMove, self).create(vals)
