#    Author: Leonardo Pistone
#    Copyright 2014 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
from openerp import api
from openerp.tests.common import TransactionCase


class TestDefaultQuantOwner(TransactionCase):

    def test_it_sets_quant_owner_on_reception(self):
        quant_domain = [('product_id', '=', self.product.id)]
        existing_quants = self.Quant.search(quant_domain)

        picking = self.chic_env['stock.picking'].create({
            'picking_type_id': self.chic_env.ref(
                'stock.chi_picking_type_in').id,
        })
        self.chic_env['stock.move'].create({
            'name': '/',
            'picking_id': picking.id,
            'product_uom': self.product.uom_id.id,
            'location_id': self.chic_env.ref(
                'stock.stock_location_suppliers').id,
            'location_dest_id': self.chic_env.ref(
                'stock.stock_location_shop0').id,
            'product_id': self.product.id,
        })
        picking.action_assign()
        picking.action_done()
        created_quant = self.Quant.search(quant_domain) - existing_quants
        self.assertEqual(1, len(created_quant))
        self.assertEqual(self.chic_user.partner_id,
                         created_quant.owner_id)

    def test_it_sets_quant_owner_on_delivery(self):
        quant_domain = [('product_id', '=', self.product.id)]
        existing_quants = self.Quant.search(quant_domain)

        picking = self.chic_env['stock.picking'].create({
            'picking_type_id': self.chic_env.ref(
                'stock.chi_picking_type_out').id,
        })
        self.chic_env['stock.move'].create({
            'name': '/',
            'picking_id': picking.id,
            'product_uom': self.product.uom_id.id,
            'location_id': self.chic_env.ref(
                'stock.stock_location_shop0').id,
            'location_dest_id': self.chic_env.ref(
                'stock.stock_location_customers').id,
            'product_id': self.product.id,
        })
        picking.action_assign()
        picking.action_done()
        created_quant = self.Quant.search(quant_domain) - existing_quants
        self.assertEqual(2, len(created_quant))
        for quant in created_quant:
            self.assertEqual(self.chic_user.partner_id,
                             quant.owner_id)

    def setUp(self):
        super(TestDefaultQuantOwner, self).setUp()
        self.partner = self.env.ref('stock.res_partner_company_1')
        self.company = self.env.ref('stock.res_company_1')
        self.chic_user = self.env['res.users'].create(
            {"partner_id": self.partner.id,
             "company_id": self.company.id,
             "company_ids": [(4, self.company.id),
                             (4, self.partner.company_id.id)],
             "login": "my_login a",
             "name": "my user",
             "groups_id": [(4, self.ref('base.group_user')),
                           (4, self.ref('stock.group_stock_manager')),
                           (4, self.ref('base.group_sale_manager'))]
             })
        self.env.ref('product.product_product_9').company_id = self.company.id
        self.chic_env = api.Environment(self.cr, self.chic_user.id, {})
        self.product = self.chic_env.ref('product.product_product_9')
        self.Quant = self.chic_env['stock.quant']
