# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.base.tests.common import BaseCommon


class TestStockLotSupplier(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")

        cls.supplier_a = cls.env["res.partner"].create(
            {"name": "Supplier A", "supplier_rank": 1}
        )
        cls.supplier_b = cls.env["res.partner"].create(
            {"name": "Supplier B", "supplier_rank": 1}
        )
        cls.non_supplier = cls.env["res.partner"].create(
            {"name": "Not a Supplier", "supplier_rank": 0}
        )

        cls.product_serial = cls.env["product.product"].create(
            {
                "name": "Serial Product",
                "is_storable": True,
                "tracking": "serial",
            }
        )
        cls.product_lot = cls.env["product.product"].create(
            {
                "name": "Lot Product",
                "is_storable": True,
                "tracking": "lot",
            }
        )

    def _create_lot(self, name, product):
        return self.env["stock.lot"].create({"name": name, "product_id": product.id})

    def _create_receipt(self, supplier, product, qty=1.0):
        picking = self.env["stock.picking"].create(
            {
                "partner_id": supplier.id,
                "picking_type_id": self.picking_type_in.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        self.env["stock.move"].create(
            {
                "picking_id": picking.id,
                "product_id": product.id,
                "product_uom_qty": qty,
                "product_uom": product.uom_id.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        picking.action_confirm()
        return picking

    def test_supplier_set_on_receipt_serial(self):
        """Validating a receipt sets the supplier on the serial number."""
        lot = self._create_lot("SN-TEST-001", self.product_serial)
        picking = self._create_receipt(self.supplier_a, self.product_serial, qty=1.0)
        picking.move_line_ids.write({"lot_id": lot.id, "quantity": 1.0})
        picking.move_ids.picked = True
        picking._action_done()

        self.assertEqual(lot.supplier_id, self.supplier_a)

    def test_supplier_set_on_receipt_lot(self):
        """Validating a receipt sets the supplier on the lot number."""
        lot = self._create_lot("LOT-TEST-001", self.product_lot)
        picking = self._create_receipt(self.supplier_a, self.product_lot, qty=5.0)
        picking.move_line_ids.write({"lot_id": lot.id, "quantity": 5.0})
        picking.move_ids.picked = True
        picking._action_done()

        self.assertEqual(lot.supplier_id, self.supplier_a)

    def test_supplier_not_overwritten_on_second_receipt(self):
        """A lot that already has a supplier keeps it when received again."""
        lot = self._create_lot("SN-TEST-002", self.product_serial)
        lot.supplier_id = self.supplier_a  # pre-set supplier

        # Receive this serial from supplier B — should NOT overwrite supplier A
        picking = self._create_receipt(self.supplier_b, self.product_serial, qty=1.0)
        picking.move_line_ids.write({"lot_id": lot.id, "quantity": 1.0})
        picking.move_ids.picked = True
        picking._action_done()

        self.assertEqual(lot.supplier_id, self.supplier_a)

    def test_supplier_not_set_on_outgoing(self):
        """Validating an outgoing transfer does not set supplier on the lot."""
        lot = self._create_lot("SN-TEST-003", self.product_serial)
        # Put stock in place without going through a receipt
        self.env["stock.quant"]._update_available_quantity(
            self.product_serial, self.stock_location, 1.0, lot_id=lot
        )

        picking_out = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type_out.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
            }
        )
        self.env["stock.move"].create(
            {
                "picking_id": picking_out.id,
                "product_id": self.product_serial.id,
                "product_uom_qty": 1.0,
                "product_uom": self.product_serial.uom_id.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
            }
        )
        picking_out.action_confirm()
        picking_out.move_line_ids.write({"lot_id": lot.id, "quantity": 1.0})
        picking_out.move_ids.picked = True
        picking_out._action_done()

        # Supplier must remain unset — outgoing should never touch it
        self.assertFalse(lot.supplier_id)

    def test_untracked_product_receipt_no_lot(self):
        """Receipts for untracked products create no lot and don't raise errors."""
        product_untracked = self.env["product.product"].create(
            {
                "name": "Untracked Product",
                "is_storable": True,
                "tracking": "none",
            }
        )
        picking = self._create_receipt(self.supplier_a, product_untracked, qty=3.0)
        picking.move_line_ids.write({"quantity": 3.0})
        picking.move_ids.picked = True
        picking._action_done()

        lots = self.env["stock.lot"].search([("product_id", "=", product_untracked.id)])
        self.assertFalse(lots)
