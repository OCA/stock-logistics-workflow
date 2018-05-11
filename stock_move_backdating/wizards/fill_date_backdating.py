# -*- coding: utf-8 -*-
# Copyright 2018 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class FillDateBackdating(models.TransientModel):
    _name = "fill.date.backdating"

    date_backdating = fields.Datetime(string='Actual Movement Date')

    @api.multi
    def fill_date_backdating(self):
        """ Fill the Actual Movement Date on all pack operations. """
        self.ensure_one()
        picking = self.env['stock.picking'].browse(self._context['active_id'])
        for pack in picking.pack_operation_product_ids:
            pack.date_backdating = self.date_backdating
        return {'type': 'ir.actions.act_window_close'}
