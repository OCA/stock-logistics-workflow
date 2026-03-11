from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestStockMoveLineDevaluation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner = cls.env["res.partner"].create(
            {"name": "Test Customer", "customer_rank": 1}
        )
        cls.pricelist = cls.env["product.pricelist"].create({"name": "Test Pricelist"})
        cls.partner.property_product_pricelist = cls.pricelist

        cls.product = cls.env["product.product"].search(
            [("detailed_type", "=", "product")], limit=1
        ) or cls.env["product.product"].search([("type", "=", "product")], limit=1)
        if not cls.product:
            raise AssertionError(
                "No stockable product found in database for test setup."
            )

        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")

    def _create_outgoing_picking(self, qty=5.0):
        """Helper to create a confirmed and done outgoing picking."""
        picking = self.env["stock.picking"].create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.picking_type_out.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
            }
        )
        move = self.env["stock.move"].create(
            {
                "name": self.product.display_name,
                "product_id": self.product.id,
                "product_uom_qty": qty,
                "product_uom": self.uom_unit.id,
                "picking_id": picking.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "picking_type_id": self.picking_type_out.id,
            }
        )
        picking.action_confirm()
        picking.action_assign()
        for ml in picking.move_line_ids:
            ml.qty_done = ml.reserved_uom_qty or qty
        picking._action_done()
        return picking, move

    def test_wizard_onchange_partner(self):
        """Test that selecting a partner sets the pricelist."""
        wizard = self.env["stock.move.line.devaluation.wizard"].create(
            {"partner_id": self.partner.id}
        )
        wizard._onchange_partner_id()
        self.assertEqual(wizard.pricelist_id, self.pricelist)

    def test_wizard_no_results_raises_error(self):
        """Test that wizard raises UserError when no lines found."""
        wizard = self.env["stock.move.line.devaluation.wizard"].create(
            {"date_from": "2099-01-01", "date_to": "2099-12-31"}
        )
        with self.assertRaises(UserError):
            wizard.action_generate_report()

    def test_report_generation(self):
        """Test that report lines are created from outgoing moves."""
        self._create_outgoing_picking(qty=5.0)

        wizard = self.env["stock.move.line.devaluation.wizard"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": self.pricelist.id,
            }
        )
        action = wizard.action_generate_report()

        report_lines = self.env["stock.move.line.devaluation.report"].search(
            action.get("domain", [])
        )
        self.assertTrue(report_lines)
        for line in report_lines:
            self.assertEqual(line.partner_id, self.partner)
            self.assertGreater(line.net_qty, 0)

    def test_return_reduces_net_qty(self):
        """Test that returns reduce the net quantity in the report."""
        picking, move = self._create_outgoing_picking(qty=5.0)

        # Create return
        return_picking = picking.copy(
            {
                "location_id": self.customer_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        move.copy(
            {
                "picking_id": return_picking.id,
                "location_id": self.customer_location.id,
                "location_dest_id": self.stock_location.id,
                "product_uom_qty": 2.0,
                "origin_returned_move_id": move.id,
            }
        )
        return_picking.action_confirm()
        return_picking.action_assign()
        for ml in return_picking.move_line_ids:
            ml.qty_done = ml.reserved_uom_qty or 2.0
        return_picking._action_done()

        wizard = self.env["stock.move.line.devaluation.wizard"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": self.pricelist.id,
            }
        )
        action = wizard.action_generate_report()

        report_lines = self.env["stock.move.line.devaluation.report"].search(
            action.get("domain", [])
        )
        self.assertTrue(report_lines)
        total_net = sum(report_lines.mapped("net_qty"))
        self.assertAlmostEqual(total_net, 3.0, places=2)

    def test_full_return_excluded(self):
        """Test that fully returned moves are excluded from report."""
        picking, move = self._create_outgoing_picking(qty=5.0)

        # Create full return
        return_picking = picking.copy(
            {
                "location_id": self.customer_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        move.copy(
            {
                "picking_id": return_picking.id,
                "location_id": self.customer_location.id,
                "location_dest_id": self.stock_location.id,
                "product_uom_qty": 5.0,
                "origin_returned_move_id": move.id,
            }
        )
        return_picking.action_confirm()
        return_picking.action_assign()
        for ml in return_picking.move_line_ids:
            ml.qty_done = ml.reserved_uom_qty or 5.0
        return_picking._action_done()

        wizard = self.env["stock.move.line.devaluation.wizard"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": self.pricelist.id,
            }
        )
        with self.assertRaises(UserError):
            wizard.action_generate_report()
