# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo.tests import SavepointCase
from odoo import fields


class TestUseDateEntry(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_quince_jam = cls.env.ref(
            'product_expiry_stock_move_line_use_date.product_quince_jam'
        )
        cls.product_cable_box = cls.env.ref(
            'stock.product_cable_management_box'
        )
        cls.picking_type_receipt = cls.env.ref('stock.picking_type_in')
        cls.location_suppliers = cls.env.ref('stock.stock_location_suppliers')
        cls.location_stock = cls.env.ref('stock.stock_location_stock')

    def _create_receipt_picking(self):
        picking = self.env['stock.picking'].create({
            'picking_type_id': self.picking_type_receipt.id,
            'location_id': self.location_suppliers.id,
            'location_dest_id': self.location_stock.id,
        })
        picking.onchange_picking_type()
        return picking

    def _create_stock_move(self, picking, product, quantity):
        return self.env['stock.move'].create({
            'name': 'Test receipt %s' % product.name,
            'picking_id': picking.id,
            'picking_type_id': picking.picking_type_id.id,
            'location_id': self.location_suppliers.id,
            'location_dest_id': self.location_stock.id,
            'product_id': product.id,
            'product_uom': product.uom_id.id,
            'product_uom_qty': quantity,
        })

    def test_display_lot_use_date_name(self):
        picking = self._create_receipt_picking()
        quince_jam_move = self._create_stock_move(
            picking, self.product_quince_jam, 10.0
        )
        cable_box_move = self._create_stock_move(
            picking, self.product_cable_box, 10.0
        )
        self.assertFalse(picking.has_use_date_text)
        picking.action_confirm()
        self.assertTrue(picking.has_use_date_text)
        self.assertEqual(picking.state, 'assigned')
        self.assertTrue(quince_jam_move.show_lots_use_date_text)
        self.assertFalse(cable_box_move.show_lots_use_date_text)
        self.assertTrue(quince_jam_move.move_line_ids.show_lots_use_date_text)
        self.assertFalse(cable_box_move.move_line_ids.show_lots_use_date_text)
        quince_jam_act = quince_jam_move.action_show_details()
        self.assertTrue(
            quince_jam_act.get('context').get('show_lots_date_use')
        )
        cable_box_act = cable_box_move.action_show_details()
        self.assertFalse(
            cable_box_act.get('context').get('show_lots_date_use')
        )

    def test_lot_use_date_name_product_lot(self):
        picking = self._create_receipt_picking()
        quince_jam_move = self._create_stock_move(
            picking, self.product_quince_jam, 10.0
        )
        picking.action_confirm()
        quince_jam_move.move_line_ids.write({
            'lot_name': '123456',
            'lot_use_date_name': '2050-01-01',
            'qty_done': 10.0,
        })
        picking.button_validate()
        quince_jam_lot = quince_jam_move.move_line_ids.lot_id
        self.assertEqual(quince_jam_lot.name, '123456')
        self.assertEqual(
            quince_jam_lot.use_date, fields.Datetime.to_datetime('2050-01-01')
        )
