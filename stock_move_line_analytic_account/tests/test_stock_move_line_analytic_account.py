from odoo.tests.common import TransactionCase


class TestStockMoveLineAnalyticAccount(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.AnalyticAccount = cls.env["account.analytic.account"]
        cls.Picking = cls.env["stock.picking"]
        cls.Move = cls.env["stock.move"]
        cls.MoveLine = cls.env["stock.move.line"]
        cls.Product = cls.env["product.product"]

        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")

        cls.analytic_plan = cls.env["account.analytic.plan"].create(
            {"name": "Test Plan"}
        )
        cls.analytic_account = cls.AnalyticAccount.create(
            {"name": "Test Analytic Account", "plan_id": cls.analytic_plan.id}
        )

        cls.product = cls.Product.search(
            [("detailed_type", "=", "product")], limit=1
        ) or cls.Product.search([("type", "=", "product")], limit=1)
        if not cls.product:
            raise AssertionError(
                "No stockable product found in database for test setup."
            )

        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})

        cls.picking = cls.Picking.create(
            {
                "partner_id": cls.partner.id,
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
                "analytic_distribution": {
                    str(cls.analytic_account.id): 100.0,
                },
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

    def test_analytic_account_is_computed(self):
        self.assertEqual(self.move_line.analytic_account_id, self.analytic_account)
        self.assertTrue(self.MoveLine._fields["analytic_account_id"].store)

    def test_search_by_analytic_account(self):
        result = self.MoveLine.search(
            [("analytic_account_id", "=", self.analytic_account.id)]
        )
        self.assertIn(self.move_line, result)

    def test_read_group_by_analytic_account(self):
        groups = self.MoveLine.read_group(
            [("id", "=", self.move_line.id)],
            ["analytic_account_id"],
            ["analytic_account_id"],
        )
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]["analytic_account_id"][0], self.analytic_account.id)

    def test_no_analytic_distribution(self):
        self.move.analytic_distribution = False
        self.move_line._compute_analytic_account_id()
        self.assertFalse(self.move_line.analytic_account_id)
