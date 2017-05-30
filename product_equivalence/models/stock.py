# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class stock_move(models.Model):
    _inherit = 'stock.move'

    def replace_equivalence(self):
        """ If a product with an equivalence is found on a
            move line, it is replaced by its equivalence."""
        for move in self:
            if move.picking_id and \
                    move.picking_id.picking_type_id.code == 'outgoing':
                if move.product_id.equivalent_id:
                    # replace_product is provided by the module
                    # packing_product_change
                    self.replace_product(move.product_id.equivalent_id.id)
        return True

    @api.model
    def create(self, vals):
        move = super(stock_move, self).create(vals)
        move.replace_equivalence()
        return move

    @api.multi
    def write(self, vals):
        res = super(stock_move, self).write(vals)
        self.replace_equivalence()
        return res
