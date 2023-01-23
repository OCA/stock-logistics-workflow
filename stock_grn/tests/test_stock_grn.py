# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class StockGrn(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.grn_model = cls.env["stock.grn"]
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "My Company",
                "email": "my@company.com",
                "company_id": False,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product",
            }
        )

    def test_grn_1(self):
        """
        This tests links a ready receipt to a Goods Received Note.
        """
        receipt_type = self.env.ref("stock.picking_type_in")
        initial_count_picking_grn = receipt_type.count_picking_grn
        picking = self.env["stock.picking"].create(
            {
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "picking_type_id": receipt_type.id,
            }
        )
        self.env["stock.move"].create(
            {
                "name": "test_grn_1",
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "product_id": self.product.id,
                "product_uom": self.uom_unit.id,
                "product_uom_qty": 1.0,
                "picking_id": picking.id,
                "picking_type_id": receipt_type.id,
            }
        )
        picking.action_confirm()
        delivery_note_supplier_number = "DN TEST"
        grn = self.grn_model.create(
            {
                "carrier_id": self.partner.id,
                "delivery_note_supplier_number": delivery_note_supplier_number,
                "picking_ids": [
                    (4, picking.id),
                ],
            }
        )

        self.assertEqual(picking.grn_id.id, grn.id)
        self.assertEqual(
            picking.delivery_note_supplier_number, delivery_note_supplier_number
        )
        # recompute count_picking_grn to check the inventory overview is updated
        receipt_type._compute_count_picking_grn()
        self.assertEqual(receipt_type.count_picking_grn, initial_count_picking_grn + 1)
