# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    @api.multi
    def check_backorder(self):
        self.ensure_one()
        # If strategy == 'manual', let the normal process going on
        if self.picking_type_id.backorder_strategy == 'manual':
            return super(StockPicking, self).check_backorder()
        return False

    @api.multi
    def _create_backorder(self, backorder_moves=None):
        if backorder_moves is None:
            backorder_moves = []
        res = False
        # Do nothing with pickings 'no_create'
        pickings = self.filtered(
            lambda p: p.picking_type_id.backorder_strategy != 'no_create')
        pickings_no_create = self - pickings
        pickings_no_create.mapped('move_lines')._cancel_remaining_quantities()
        backorders = super(StockPicking, pickings)._create_backorder(
            backorder_moves=backorder_moves)
        to_cancel = backorders.filtered(
            lambda b: b.backorder_id.picking_type_id.backorder_strategy ==
            'cancel')
        to_cancel.action_cancel()
        return res
