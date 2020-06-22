# coding: utf-8
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import Warning as UserError


class StockMove(models.Model):
    _inherit = 'stock.move'

    show_quick_quantity_done = fields.Boolean(
        default=False,
        compute='_compute_show_quick_quantity_done',
        help='Technical field used to compute whether the quick quantity'
             ' done button should be shown.')

    @api.multi
    def _compute_show_quick_quantity_done(self):
        for move in self:
            if move.quantity_done < move.product_uom_qty:
                move.show_quick_quantity_done = True

    @api.multi
    def quick_quantity_done(self):
        for move in self:
            initial_demand = move.product_uom_qty
            if initial_demand:
                move.quantity_done = initial_demand
                self._quantity_done_set()
            else:
                raise UserError(_(
                    "We can't quickly set quantity done because there's no "
                    "initial demand or it's null."))
