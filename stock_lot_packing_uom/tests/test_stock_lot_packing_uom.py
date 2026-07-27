# Copyright 2026 Abubakarafghan
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestStockLotPackingUom(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.uom_dozen = cls.env.ref("uom.product_uom_dozen")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Pack Tracked Product",
                "type": "consu",
                "is_storable": True,
                "tracking": "lot",
                "uom_id": cls.uom_unit.id,
                "uom_po_id": cls.uom_dozen.id,
                "auto_create_lot": True,
            }
        )
        cls.vendor = cls.env["res.partner"].create({"name": "Vendor Packing"})
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.picking_type_in = cls.warehouse.in_type_id
        cls.picking_type_in.auto_create_lot = True

    def _create_incoming_picking(self, product_uom, qty):
        picking = self.env["stock.picking"].create(
            {
                "partner_id": self.vendor.id,
                "picking_type_id": self.picking_type_in.id,
                "location_id": self.picking_type_in.default_location_src_id.id,
                "location_dest_id": self.picking_type_in.default_location_dest_id.id,
            }
        )
        move = self.env["stock.move"].create(
            {
                "name": self.product.name,
                "product_id": self.product.id,
                "product_uom": product_uom.id,
                "product_uom_qty": qty,
                "picking_id": picking.id,
                "location_id": picking.location_id.id,
                "location_dest_id": picking.location_dest_id.id,
            }
        )
        picking.action_confirm()
        return picking, move

    def test_auto_create_lot_stores_packing_info(self):
        picking, move = self._create_incoming_picking(self.uom_dozen, 2.0)
        self.assertTrue(move.move_line_ids)
        line = move.move_line_ids[0]
        line.quantity = 24.0
        line.product_uom_id = self.uom_unit
        self.assertFalse(line.lot_id)
        picking.button_validate()
        self.assertTrue(line.lot_id)
        self.assertEqual(line.lot_id.packing_uom_id, self.uom_dozen)
        self.assertAlmostEqual(line.lot_id.received_qty, 2.0)

    def test_existing_lot_gets_packing_info(self):
        lot = self.env["stock.lot"].create(
            {
                "name": "LOT-MANUAL-001",
                "product_id": self.product.id,
                "company_id": self.env.company.id,
            }
        )
        picking, move = self._create_incoming_picking(self.uom_dozen, 1.0)
        line = move.move_line_ids[0]
        line.quantity = 12.0
        line.product_uom_id = self.uom_unit
        line.lot_id = lot
        picking.button_validate()
        self.assertEqual(lot.packing_uom_id, self.uom_dozen)
        self.assertAlmostEqual(lot.received_qty, 1.0)

    def test_quant_packing_qty(self):
        lot = self.env["stock.lot"].create(
            {
                "name": "LOT-PACK-001",
                "product_id": self.product.id,
                "company_id": self.env.company.id,
                "packing_uom_id": self.uom_dozen.id,
                "received_qty": 1.0,
            }
        )
        quant = self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "lot_id": lot.id,
                "quantity": 12.0,
            }
        )
        self.assertEqual(quant.packing_uom_id, self.uom_dozen)
        self.assertAlmostEqual(quant.packing_qty, 1.0)
