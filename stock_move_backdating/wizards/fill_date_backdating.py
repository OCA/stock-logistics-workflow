# -*- coding: utf-8 -*-
# Copyright 2018 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from ..models.stock_pack_operation import check_date


class FillDateBackdating(models.TransientModel):
    _name = "fill.date.backdating"

    date_backdating = fields.Datetime(string='Actual Movement Date')

    @api.onchange('date_backdating')
    def onchange_date_backdating(self):
        check_date(self.date_backdating)

    @api.multi
    def fill_date_backdating(self):
        """ Fill the Actual Movement Date on all pack operations. """
        self.ensure_one()
        picking = self.env['stock.picking'].browse(self._context['active_id'])
        picking.pack_operation_product_ids.write(
            {'date_backdating': self.date_backdating})
        return {'type': 'ir.actions.act_window_close'}
