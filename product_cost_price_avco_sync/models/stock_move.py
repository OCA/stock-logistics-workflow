# Copyright 2019 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields, models
from odoo.tools.float_utils import float_compare


class StockMove(models.Model):
    _inherit = 'stock.move'

    def write(self, vals):
        """ Update cost price avco """
        res = super(StockMove, self).write(vals)
        if (('price_unit' in vals or 'quantity_done' in vals) and
                not self.env.context.get('skip_avco_sync')):
            self.cost_price_avco_sync()
        return res

    def _create_price_history(self, value):
        self.env['product.price.history'].create([{
            'product_id': move.product_id.id,
            'cost': value,
            'datetime': move.date,
            'company_id': move.company_id.id,
        } for move in self])

    def _previous_instant_date(self):
        """ Returns previous instant before move was done"""
        self.ensure_one()
        date_with_delta = fields.Datetime.from_string(
            self.date) - timedelta(seconds=1)
        return fields.Datetime.to_string(date_with_delta)

    def _remove_after_history_price(self):
        PriceHistory = self.env['product.price.history']
        for move in self:
            PriceHistory.search([
                ('company_id', '=', move.company_id.id),
                ('product_id', '=', move.product_id.id),
                ('datetime', '>=', move.date),
            ]).unlink()

    def get_average_price(self, previous_qty, previous_price):
        if self.quantity_done == 0.0:
            price = previous_price
        elif previous_qty < 0.0:
            price = self.price_unit
        else:
            price = ((previous_qty * previous_price) +
                     (self.quantity_done * self.price_unit)
                     ) / (previous_qty + self.quantity_done)
        return price

    def cost_price_avco_sync(self):
        procesed_moves = set()
        for move in self.sorted('date'):
            if (move.id in procesed_moves or move.state != 'done' or
                    not move._is_in() or
                    move.product_id.cost_method != 'average'):
                continue
            previous_instant = move._previous_instant_date()
            previous_qty = move.product_id.with_context(
                to_date=previous_instant
            ).qty_available
            previous_price = move.product_id.get_history_price(
                move.company_id.id, previous_instant)
            price = move.get_average_price(previous_qty, previous_price)
            move._remove_after_history_price()
            move._create_price_history(price)
            previous_qty += move.quantity_done
            affected_moves = self.with_context(skip_avco_sync=True).search([
                ('product_id', '=', move.product_id.id),
                ('date', '>', move.date),
            ], order='date')
            for af_move in affected_moves:
                if af_move._is_in():
                    if af_move.inventory_id or af_move.move_orig_ids:
                        af_move.write({
                            'price_unit': price,
                            'value': price * af_move.quantity_done,
                        })
                    # Avoid reprocess move if included in self.write
                    procesed_moves.add(af_move.id)
                    price = af_move.get_average_price(previous_qty, price)
                    af_move._create_price_history(price)
                    previous_qty += af_move.quantity_done
                elif af_move._is_out():
                    af_move.write({
                        'price_unit': -price,
                        'value': -price * af_move.quantity_done,
                    })
                    previous_qty -= af_move.quantity_done
            if float_compare(move.product_id.standard_price, price,
                             precision_rounding=move.product_uom.rounding):
                # Write the standard price, as SUPERUSER_ID because a warehouse
                # manager may not have the right to write on products
                move.product_id.with_context(
                    force_company=move.company_id.id,
                ).sudo().write({'standard_price': price})
