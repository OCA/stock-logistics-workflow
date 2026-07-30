from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestStockMoveLineDevaluation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.partner = cls.env["res.partner"].create(
            {"name": "Test Devaluation Customer"}
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
                "standard_price": 5.0,
            }
        )

        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")

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
        """Create a return for a picking manually linking returned moves."""
        return_type = picking.picking_type_id.return_picking_type_id or (
            picking.picking_type_id
        )
        return_picking = self.env["stock.picking"].create(
            {
                "partner_id": picking.partner_id.id,
                "picking_type_id": return_type.id,
                "location_id": picking.location_dest_id.id,
                "location_dest_id": picking.location_id.id,
                "origin": "Return of %s" % picking.name,
            }
        )
        original_move = picking.move_ids[0]
        self.env["stock.move"].create(
            {
                "name": "Return of %s" % original_move.name,
                "product_id": self.product.id,
                "product_uom_qty": qty,
                "product_uom": self.uom_unit.id,
                "picking_id": return_picking.id,
                "location_id": picking.location_dest_id.id,
                "location_dest_id": picking.location_id.id,
                "origin_returned_move_id": original_move.id,
            }
        )
        return_picking.action_confirm()
        return_picking.action_assign()
        for ml in return_picking.move_line_ids:
            ml.qty_done = ml.reserved_uom_qty or qty
        return_picking._action_done()
        return return_picking

    def _create_wizard(self, **kwargs):
        """Helper to create the devaluation wizard."""
        return self.env["stock.move.line.devaluation.wizard"].create(kwargs)

    def test_wizard_onchange_partner(self):
        """Test that selecting a partner sets the pricelist."""
        wizard = self._create_wizard(partner_id=self.partner.id)
        wizard._onchange_partner_id()
        self.assertEqual(wizard.pricelist_id, self.pricelist)

    def test_wizard_onchange_no_partner(self):
        """Test that onchange without partner does not crash."""
        wizard = self._create_wizard()
        wizard._onchange_partner_id()
        self.assertFalse(wizard.pricelist_id)

    def test_wizard_no_results_raises_error(self):
        """Test that wizard raises UserError when no lines found."""
        wizard = self._create_wizard(date_from="2099-01-01", date_to="2099-12-31")
        with self.assertRaises(UserError):
            wizard.action_generate_report()

    def test_report_generation(self):
        """Test that report lines are created from outgoing moves."""
        self._create_outgoing_picking(qty=5.0)
        wizard = self._create_wizard(
            partner_id=self.partner.id,
            pricelist_id=self.pricelist.id,
        )
        action = wizard.action_generate_report()
        report_lines = self.env["stock.move.line.devaluation.report"].search(
            action.get("domain", [])
        )
        self.assertTrue(report_lines)
        for line in report_lines:
            self.assertEqual(line.partner_id, self.partner)
            self.assertGreater(line.net_qty, 0)

    def test_report_without_partner(self):
        """Test report generation without filtering by partner."""
        self._create_outgoing_picking(qty=3.0)
        wizard = self._create_wizard()
        action = wizard.action_generate_report()
        report_lines = self.env["stock.move.line.devaluation.report"].search(
            action.get("domain", [])
        )
        self.assertTrue(report_lines)

    def test_report_without_pricelist_uses_lst_price(self):
        """Test that report uses lst_price when no pricelist set."""
        self._create_outgoing_picking(qty=2.0)
        wizard = self._create_wizard(partner_id=self.partner.id)
        action = wizard.action_generate_report()
        report_lines = self.env["stock.move.line.devaluation.report"].search(
            action.get("domain", [])
        )
        self.assertTrue(report_lines)
        for line in report_lines:
            self.assertAlmostEqual(line.unit_price, self.product.lst_price, places=2)

    def test_report_has_standard_price(self):
        """Test that report lines include the product cost."""
        self._create_outgoing_picking(qty=1.0)
        wizard = self._create_wizard(partner_id=self.partner.id)
        action = wizard.action_generate_report()
        report_lines = self.env["stock.move.line.devaluation.report"].search(
            action.get("domain", [])
        )
        self.assertTrue(report_lines)
        for line in report_lines:
            self.assertAlmostEqual(line.standard_price, 5.0, places=2)

    def test_report_has_responsible(self):
        """Test that report lines include the picking responsible."""
        picking = self._create_outgoing_picking(qty=1.0)
        picking.sudo().write({"user_id": self.env.uid})
        wizard = self._create_wizard(partner_id=self.partner.id)
        action = wizard.action_generate_report()
        report_lines = self.env["stock.move.line.devaluation.report"].search(
            action.get("domain", [])
        )
        self.assertTrue(report_lines)
        self.assertEqual(report_lines[0].responsible_id.id, self.env.uid)

    def test_report_total_value(self):
        """Test that total_value equals net_qty * unit_price."""
        self._create_outgoing_picking(qty=4.0)
        wizard = self._create_wizard(partner_id=self.partner.id)
        action = wizard.action_generate_report()
        report_lines = self.env["stock.move.line.devaluation.report"].search(
            action.get("domain", [])
        )
        for line in report_lines:
            expected = line.net_qty * line.unit_price
            self.assertAlmostEqual(line.total_value, expected, places=2)

    def test_report_with_date_range(self):
        """Test report generation with date range filters."""
        self._create_outgoing_picking(qty=5.0)
        wizard = self._create_wizard(
            partner_id=self.partner.id,
            date_from="2000-01-01",
            date_to="2000-12-31",
        )
        with self.assertRaises(UserError):
            wizard.action_generate_report()

    def test_return_reduces_net_qty(self):
        """Test that returns reduce the net quantity in the report."""
        picking = self._create_outgoing_picking(qty=5.0)
        self._create_return(picking, 2.0)
        wizard = self._create_wizard(
            partner_id=self.partner.id,
            pricelist_id=self.pricelist.id,
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
        wizard = self._create_wizard(
            partner_id=self.partner.id,
            pricelist_id=self.pricelist.id,
        )
        with self.assertRaises(UserError):
            wizard.action_generate_report()

    def test_clears_previous_report(self):
        """Test that generating report clears previous results."""
        self._create_outgoing_picking(qty=5.0)
        wizard = self._create_wizard(partner_id=self.partner.id)
        wizard.action_generate_report()
        first_count = self.env["stock.move.line.devaluation.report"].search_count(
            [("create_uid", "=", self.env.uid)]
        )

        # Generate again
        wizard2 = self._create_wizard(partner_id=self.partner.id)
        wizard2.action_generate_report()
        second_count = self.env["stock.move.line.devaluation.report"].search_count(
            [("create_uid", "=", self.env.uid)]
        )

        self.assertEqual(first_count, second_count)

    def test_analytic_account_without_module(self):
        """Test analytic account extraction when field may not exist."""
        self._create_outgoing_picking(qty=1.0)
        wizard = self._create_wizard(partner_id=self.partner.id)
        action = wizard.action_generate_report()
        report_lines = self.env["stock.move.line.devaluation.report"].search(
            action.get("domain", [])
        )
        # Should work without error even without analytic_distribution
        self.assertTrue(report_lines)
        for line in report_lines:
            # May be False if stock_analytic not installed
            self.assertFalse(line.analytic_account_id)
