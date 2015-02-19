# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Agile Business Group sagl (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp.addons.stock.tests.common import TestStockCommon


class TestCancelPicking(TestStockCommon):

    def test_cancel_picking(self):
        picking_out = self.PickingObj.create({
            'partner_id': self.partner_agrolite_id,
            'picking_type_id': self.picking_type_out})
        self.MoveObj.create({
            'name': self.productA.name,
            'product_id': self.productA.id,
            'product_uom_qty': 1,
            'product_uom': self.productA.uom_id.id,
            'picking_id': picking_out.id,
            'location_id': self.stock_location,
            'location_dest_id': self.customer_location})
        picking_out.action_confirm()
        picking_out.action_assign()
        picking_out.do_transfer()
        quants = self.StockQuantObj.search([
            ('product_id', '=', self.productA.id),
            ('location_id', '=', self.stock_location)
            ])
        total_qty = [quant.qty for quant in quants]
        self.assertEqual(
            sum(total_qty), -1,
            'Expecting -1 Unit , got %.4f Unit on location stock!' % (
                sum(total_qty)))
        picking_out.action_revert_done()
        quants = self.StockQuantObj.search([
            ('product_id', '=', self.productA.id),
            ('location_id', '=', self.stock_location)
            ])
        total_qty = [quant.qty for quant in quants]
        self.assertEqual(
            sum(total_qty), 0,
            'Expecting 0 Unit , got %.4f Unit on location stock!' % (
                sum(total_qty)))
