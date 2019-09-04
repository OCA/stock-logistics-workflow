# -*- coding: utf-8 -*-
# Copyright (C) 2018 Akretion (<http://www.akretion.com>)
# @author: Florian da Costa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_ship_create(self):
        dropshipping_route = self.env.ref(
            'stock_dropshipping.route_drop_shipping')
        line_obj = self.env['sale.order.line']
        supplier_dropshipping = {}
        supplier_line = {}
        for line in self.order_line:
            supplier = line._get_product_supplier()
            if not supplier:
                continue
            if (line.route_id and line.route_id == dropshipping_route) or \
                    dropshipping_route.id in line.product_id.route_ids.ids:
                supplier_dropshipping[supplier.id] = (
                    supplier_dropshipping.get('supplier.id', line_obj) + line)
            elif not line.route_id and supplier.allow_whole_order_dropshipping:
                supplier_line[supplier.id] = (
                    supplier_line.get(supplier.id, line_obj) + line)

        for supplier_id, line in supplier_dropshipping.iteritems():
            lines_to_dropshipping = supplier_line.get(supplier_id)
            if lines_to_dropshipping:
                lines_to_dropshipping.write(
                    {'route_id': dropshipping_route.id})
        return super(SaleOrder, self).action_ship_create()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _get_product_supplier(self):
        ''' returns the main supplier of sale order line '''
        self.ensure_one()
        supplierinfo = self.env['product.supplierinfo']
        company_supplier = supplierinfo.search(
            [('product_tmpl_id', '=', self.product_id.product_tmpl_id.id),
             ('company_id', '=', self.company_id.id)], limit=1)
        if company_supplier:
            return company_supplier.name
        return self.product_id.seller_id
