# -*- coding: utf-8 -*-
# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def _prepare_sale_order(self, picking):
        return {
            'partner_id': picking.partner_id.id,
            'origin': picking.name,
        }

    @api.model
    def _prepare_sale_order_line(self, order, move):
        return {
            'product_id': move.product_id.id,
            'product_uom_qty': move.product_uom_qty,
            'order_id': order.id,
        }

    @api.multi
    def create_sale_order(self):
        SaleOrder = self.env['sale.order']
        SaleOrderLine = self.env['sale.order.line']
        pickings = self.filtered(lambda x: x.state != 'done' and x.partner_id)
        new_orders = SaleOrder
        for pick in pickings:
            order_vals = self._prepare_sale_order(pick)
            order_vals.update(
                SaleOrder.onchange_partner_id(order_vals['partner_id']).get(
                    'value', {}))
            order = SaleOrder.create(order_vals)
            for move in pick.move_lines:
                line_vals = self._prepare_sale_order_line(order, move)
                line_vals.update(
                    SaleOrderLine.product_id_change(
                        order_vals.get('pricelist_id', False),
                        line_vals['product_id'],
                        qty=line_vals['product_uom_qty'],
                        partner_id=order_vals['partner_id'],
                        fiscal_position=order.fiscal_position.id,
                    ).get('value', {}))
                if line_vals.get('tax_id'):
                    line_vals['tax_id'] = [(6, 0, line_vals['tax_id'])]
                SaleOrderLine.create(line_vals)
            new_orders |= order
        pickings.action_cancel()
        return new_orders

    @api.multi
    def button_create_sale(self):
        new_orders = self.create_sale_order()
        res = self.env.ref('sale.action_quotations').read()[0]
        if len(new_orders) == 1:
            res['res_id'] = new_orders.id
            res['view_mode'] = 'form'
            res['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
        else:
            res['domain'] = [('id', 'in', new_orders.ids)]
            res['view_mode'] = 'tree,form'
        return res
