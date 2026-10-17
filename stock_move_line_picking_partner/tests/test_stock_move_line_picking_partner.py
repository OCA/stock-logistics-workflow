from odoo.tests.common import TransactionCase


class TestStockMoveLinePickingPartner(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.Partner = cls.env["res.partner"]
        cls.Picking = cls.env["stock.picking"]
        cls.Move = cls.env["stock.move"]
        cls.MoveLine = cls.env["stock.move.line"]
        cls.Product = cls.env["product.product"]

        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")

        cls.partner_1 = cls.Partner.create({"name": "Customer A"})
        cls.partner_2 = cls.Partner.create({"name": "Customer B"})

        cls.product = cls.Product.search(
            [("detailed_type", "=", "product")], limit=1
        ) or cls.Product.search([("type", "=", "product")], limit=1)
        if not cls.product:
            raise AssertionError(
                "No stockable product found in database for test setup."
            )

        cls.picking = cls.Picking.create(
            {
                "partner_id": cls.partner_1.id,
                "picking_type_id": cls.picking_type_out.id,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
            }
        )

        cls.move = cls.Move.create(
            {
                "name": cls.product.display_name,
                "product_id": cls.product.id,
                "product_uom_qty": 5.0,
                "product_uom": cls.uom_unit.id,
                "picking_id": cls.picking.id,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
                "picking_type_id": cls.picking_type_out.id,
            }
        )

        cls.move_line = cls.MoveLine.create(
            {
                "picking_id": cls.picking.id,
                "move_id": cls.move.id,
                "product_id": cls.product.id,
                "product_uom_id": cls.uom_unit.id,
                "qty_done": 2.0,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
            }
        )

    def test_picking_partner_is_stored_related(self):
        self.assertEqual(self.move_line.picking_partner_id, self.partner_1)
        self.assertTrue(self.MoveLine._fields["picking_partner_id"].store)

    def test_search_by_picking_partner(self):
        result = self.MoveLine.search([("picking_partner_id", "=", self.partner_1.id)])
        self.assertIn(self.move_line, result)

    def test_read_group_by_picking_partner(self):
        groups = self.MoveLine.read_group(
            [("id", "=", self.move_line.id)],
            ["picking_partner_id"],
            ["picking_partner_id"],
        )
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]["picking_partner_id"][0], self.partner_1.id)
