# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2015 Camptocamp SA
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
#
##############################################################################

from openerp.tests import common


class TestSaleTeamRoute(common.TransactionCase):

    def setUp(self):
        super(TestSaleTeamRoute, self).setUp()
        self.sale_order_model = self.env['sale.order']
        self.sale_line_model = self.env['sale.order.line']
        self.product = self.env.ref('product.product_product_7')
        self.partner = self.env.ref('base.res_partner_1')
        self.sales_team = self.env.ref('sales_team.crm_case_section_1')
        self.route = self.env['stock.location.route'].create({
            'name': 'Test Route',
            'section_selectable': True,
        })
        self.line_route = self.env['stock.location.route'].create({
            'name': 'Line Test Route',
        })

    def test_sales_team_route(self):
        self.sales_team.route_id = self.route
        order = self.sale_order_model.create({
            'partner_id': self.partner.id,
            'section_id': self.sales_team.id,
        })
        line = self.sale_line_model.create({
            'order_id': order.id,
            'product_id': self.product.id,
            'product_uom_qty': 1,
        })
        order.action_button_confirm()
        procurement = line.procurement_ids
        self.assertEquals(procurement.route_ids, self.route)

    def test_sales_team_route_line_has_priority(self):
        self.sales_team.route_id = self.route
        order = self.sale_order_model.create({
            'partner_id': self.partner.id,
            'section_id': self.sales_team.id,
        })
        line = self.sale_line_model.create({
            'order_id': order.id,
            'product_id': self.product.id,
            'product_uom_qty': 1,
            'route_id': self.line_route.id,
        })
        order.action_button_confirm()
        procurement = line.procurement_ids
        self.assertEquals(procurement.route_ids, self.line_route)
