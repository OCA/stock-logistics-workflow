# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
###############################################################################
#    Coded by: Sergio Ernesto Tostado Sánchez (sergio@vauxoo.com)
###############################################################################
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
###############################################################################

from openerp.tests.common import TransactionCase
from openerp.osv.orm import except_orm


class TestUnicity(TransactionCase):

    """
    This test will prove the next cases to procure the
    module unicity:
    - Test 1: Can't be created two Serial Numbers with the same name
    """

    def setUp(self):
        super(TestUnicity, self).setUp()
        self.stock_production_lot_obj = self.env["stock.production.lot"]
        self.product_obj = self.env["product.product"]

    def test_1_creating_two_equal_serial_numbers(self):
        """
        Test 1. Creating 2 equal serial numbers
        """
        product_id = self.env.ref('product_unique_serial.product_demo_1')
        print product_id
        sucessful = False
        lot_data = {'name': '86137801852519', 'product_id': product_id.id}
        try:
            self.stock_production_lot_obj.create(lot_data)
            self.stock_production_lot_obj.create(lot_data)
        except except_orm:
            sucessful = True
        self.assertTrue(
            sucessful, "ERROR: The module can create duplicated "
            "serial numbers, which is a problem that should be attended...")
