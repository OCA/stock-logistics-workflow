# -*- coding: utf-8 -*-
# © 2016  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import openerp.tests.common as common


class TestChangeProduct(common.TransactionCase):

    def test_product_change_qty(self):
        """ Inventory product quantity to 3
            Check product quantity is 3
            Change product quantity to 5
            Check product quantity is 5
        """

        myProduct = self.env.ref('product.product_product_37')
        myLocation = self.env.ref('stock.stock_location_14')

        inventory = self.env['stock.inventory'].create(
            {'name': 'Inventory Product %s' % myProduct.name})
        self.env['stock.inventory.line'].create(
            {'inventory_id': inventory.id,
             'product_id': myProduct.id,
             'product_uom_id': self.env.ref('product.product_uom_unit').id,
             'product_qty': 3,
             'location_id': myLocation.id
             })
        inventory.action_done()
        self.assertEqual(myProduct.qty_available, 3)

        wizard_model = self.env['stock.change.product.qty']
        wizard = wizard_model.create({'product_id': myProduct.id,
                                      'location_id': myLocation.id,
                                      'new_quantity': 5})
        wizard.change_product_qty()
        self.assertEqual(myProduct.qty_available, 5)
