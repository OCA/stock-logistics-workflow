# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from uuid import uuid4
from odoo.tests.common import TransactionCase


class TestSaleOrderDeliveryNote(TransactionCase):
    """
    Tests about the delivery note provided by the customer.
    This field should by passed into the related picking.
    """

    def setUp(self):
        super(TestSaleOrderDeliveryNote, self).setUp()
        self.partner = self.env.ref('base.res_partner_2')
        self.product = self.env.ref('product.product_product_4')
        self.sale_obj = self.env['sale.order']

    def create_sale_order(self):
        """
        Create a new sale order
        :return: sale.order recordset
        """
        values = {
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom': self.product.uom_id.id,
                'price_unit': self.product.list_price,
                'product_uom_qty': 1,
            })],
        }
        return self.sale_obj.create(values)

    def test_update_delivery_note_filled(self):
        """
        Create a new sale order with a delivery_note value and check if
        pickings have this info too.
        :return:
        """
        sale_order = self.create_sale_order()
        sale_order.write({
            'delivery_note': str(uuid4()),
        })
        sale_order.action_confirm()
        self._check_related_picking(sale_order)
        return

    def test_update_delivery_note_empty(self):
        """
        Create a new sale order with an empty delivery_note value and check if
        pickings have this info too.
        :return:
        """
        sale_order = self.create_sale_order()
        # Force a False value
        sale_order.write({
            'delivery_note': False,
        })
        sale_order.action_confirm()
        self._check_related_picking(sale_order)
        return

    def _check_related_picking(self, sale_order):
        """
        Check if picking related to this sale order have a correct
        delivery note
        :param sale_order: sale.order recordset
        :return: bool
        """
        pickings = sale_order.picking_ids
        # We should have at least 1 picking for this test
        self.assertTrue(pickings)
        for picking in pickings:
            self.assertEquals(picking.delivery_note, sale_order.delivery_note)
        return True
