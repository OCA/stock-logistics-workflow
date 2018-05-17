# -*- coding: utf-8 -*-
# Copyright 2012 Andrea Cometa
# Copyright 2013 Agile Business Group sagl
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, models, exceptions, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def action_revert_done(self):
        for picking in self:
            sale_lines = picking.group_id.procurement_ids.mapped(
                'sale_line_id')
            if sale_lines:
                order = sale_lines[0].order_id
                delivery_line = order.with_context(
                    reopen_picking=True).order_line.filtered(
                    lambda s: s.is_delivery)
                delivery_line.unlink()
        res = super(StockPicking, self).action_revert_done()
        return res
