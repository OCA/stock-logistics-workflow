# Copyright 2019 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools.float_utils import float_compare


class StockMove(models.Model):
    _inherit = 'stock.move'

    def write(self, vals):
        res = super(StockMove, self).write(vals)
        if ('price_unit' in vals and
                not self.env.context.get('skip_cost_update')):
            self.price_unit_update()
        return res

    def price_unit_update(self):
        procesed_moves = []
        for move in self.sorted('date'):
            if (move.id in procesed_moves or move.state != 'done' or
                    not move._is_in() or
                    move.product_id.cost_method != 'average'):
                continue
            # not take in account move's quantities
            previous_qty = move.product_id.with_context(
                to_date=move.date
            ).qty_available - move.quantity_done
            price_history = self.product_id.get_cost_history_date(move.date)
            price = move.get_average_price(previous_qty, price_history)
            previous_qty += move.quantity_done
            affected_moves = self.search([
                ('product_id', '=', move.product_id.id),
                ('date', '>', move.date),
            ], order='date')
            for af_move in affected_moves:
                if af_move._is_in():
                    if af_move.inventory_id or af_move.move_orig_ids:
                        af_move.with_context(
                            skip_cost_update=True).price_unit = price
                    # Avoid reprocess move if included in self.write
                    if af_move.id not in procesed_moves:
                        procesed_moves.append(af_move.id)
                    price = af_move.get_average_price(previous_qty, price)
                    previous_qty += af_move.quantity_done
                elif af_move._is_out():
                    af_move.with_context(
                        skip_cost_update=True).price_unit = -price
                    previous_qty -= af_move.quantity_done
                    if previous_qty < 0.0:
                        previous_qty = 0.0
            if float_compare(move.product_id.standard_price, price,
                             precision_rounding=move.product_uom.rounding):
                # Write the standard price, as SUPERUSER_ID because a warehouse
                # manager may not have the right to write on products
                move.product_id.with_context(
                    force_company=move.company_id.id,
                ).sudo().write({'standard_price': price})

    def get_average_price(self, previous_qty, previous_price):
        new_std_price = ((previous_qty * previous_price) + (
            self.price_unit * self.quantity_done)) / (previous_qty +
                                                      self.quantity_done)
        return new_std_price
