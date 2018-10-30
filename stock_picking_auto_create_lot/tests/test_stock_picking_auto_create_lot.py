# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import SavepointCase


class TestStockPickingAutoCreateLot(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref('stock.warehouse0')
        cls.picking_type_in = cls.env.ref('stock.picking_type_in')
        cls.supplier_location = cls.env.ref('stock.stock_location_suppliers')
        cls.supplier = cls.env['res.partner'].create({
            'name': 'Supplier - test',
            'supplier': True,
        })
        cls.product = cls.env['product.product'].create({
            'name': 'test',
            'type': 'product',
            'tracking': 'lot',
            'auto_create_lot': True,
        })
        cls.picking = cls.env['stock.picking'].with_context(
            default_picking_type_id=cls.picking_type_in.id
        ).create({
            'partner_id': cls.supplier.id,
            'picking_type_id': cls.picking_type_in.id,
            'location_id': cls.supplier_location.id,
        })
        cls.move = cls.env['stock.move'].create({
            'name': 'test-auto-lot',
            'product_id': cls.product.id,
            'picking_id': cls.picking.id,
            'picking_type_id': cls.picking_type_in.id,
            'product_uom_qty': 2.0,
            'product_uom': cls.product.uom_id.id,
            'location_id': cls.supplier_location.id,
            'location_dest_id':
                cls.picking_type_in.default_location_dest_id.id,
        })

    def test_auto_create_lot(self):
        self.picking_type_in.auto_create_lot = True
        self.picking.action_assign()
        self.picking.button_validate()
        lot = self.env['stock.production.lot'].search([
            ('product_id', '=', self.product.id),
        ])
        self.assertEqual(len(lot), 1)
