from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestStockMoveLineDevaluation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner = cls.env["res.partner"].create(
            {"name": "Test Devaluation Customer", "customer_rank": 1}
        )
        cls.pricelist = cls.env["product.pricelist"].create(
            {"name": "Test Devaluation Pricelist"}
        )
        cls.partner.property_product_pricelist = cls.pricelist

        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Devaluation Product",
                "detailed_type": "product",
                "lst_price": 10.0,
            }
        )

        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")

        # Ensure stock availability
        cls.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": cls.product.id,
                "location_id": cls.stock_location.id,
                "inventory_quantity": 100.0,
            }
        ).action_apply_inventory()

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
        self.env["stock.move"].create(
            {
                "name": self.product.display_name,
                "product_id": self.product.id,
                "product_uom_qty": qty,
                "product_uom": self.uom_unit.id,
                "picking_id": picking.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
            }
        )
        picking.action_confirm()
        picking.action_assign()
        for ml in picking.move_line_ids:
            ml.qty_done = ml.reserved_uom_qty or qty
        picking._action_done()
        return picking

    def _create_return(self, picking, qty):
        """Create a return for a picking using the stock return wizard."""
        return_wizard = (
            self.env["stock.return.picking"]
            .with_context(active_id=picking.id, active_model="stock.picking")
            .create({})
        )
        for line in return_wizard.product_return_moves:
            if line.product_id == self.product:
                line.quantity = qty
        result = return_wizard.create_returns()
        return_picking = self.env["stock.picking"].browse(result["res_id"])
        for ml in return_picking.move_line_ids:
            ml.qty_done = qty
        return_picking._action_done()
        return return_picking

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
        picking = self._create_outgoing_picking(qty=5.0)
        self._create_return(picking, 2.0)
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
        picking = self._create_outgoing_picking(qty=5.0)
        self._create_return(picking, 5.0)
        wizard = self.env["stock.move.line.devaluation.wizard"].create(
            {
                "partner_id": self.partner.id,
                "pricelist_id": self.pricelist.id,
            }
        )
        with self.assertRaises(UserError):
            wizard.action_generate_report()
