# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from .common import Common


class TestMtsAsMtoBom(Common):
    def test_purchase_components(self):
        # Kit : pas achetable, vendable
        # Rideau : achetable, vendable
        # Lit : article MTO, achetable, vendable
        # SO pour kit => PO généré pour Lit
        product = self.product_bed_with_curtain
        purchase_orders_before = self.purchase_order_model.search([])
        order = self.create_sale_order(product)
        order.action_confirm()
        purchase_orders_after = self.purchase_order_model.search(
            [("id", "not in", purchase_orders_before.ids)]
        )
        self.assertTrue(purchase_orders_after)
        # As only the structure is MTO, generated PO should only contain the bed structure
        purchase_lines = purchase_orders_after.order_line
        self.assertEqual(purchase_lines.product_qty, 5.0)
        self.assertEqual(purchase_lines.product_id, self.product_bed_structure)

    def test_purchase_parent_kit_single_level(self):
        # Use Case 2 : purchase kit
        # Lit : kit MTO, achetable, vendable
        # Frame : pas achetable, pas vendable
        # Echelle : pas achetable, pas vendable
        # Matelas : pas achetable, pas vendable
        # SO pour lit => PO généré pour Lit
        # Use Case 3 : multi-level bom
        # Office Furniture : MTO saleable, buyable
        #   - Office Desk : 1x, not saleable, not buyable
        #   - Office Chair : 2x, not saleable, not buyable
        #   - Office Bin : 3x, not saleable, buyable
        # Ordering Office Furniture should create a PO for Office Furniture
        product = self.product_office_furniture
        purchase_orders_before = self.purchase_order_model.search([])
        order = self.create_sale_order(product)
        order.action_confirm()
        purchase_orders_after = self.purchase_order_model.search(
            [("id", "not in", purchase_orders_before.ids)]
        )
        self.assertTrue(purchase_orders_after)
        # As only one of the components is purchaseable and the BOM is,
        # there should be only one line for the BOM in the PO
        purchase_lines = purchase_orders_after.order_line
        self.assertEqual(len(purchase_lines), 1.0)
        self.assertEqual(purchase_lines.product_qty, 5.0)
        self.assertEqual(purchase_lines.product_id, self.product_office_furniture)

    def test_purchase_parent_kit_multi_level(self):
        # Use Case 3 : multi-level bom
        # Garden Furniture : saleable, not buyable
        #   - Garden Chair : MTO, 4x, saleable, buyable
        #   - Garden Table : MTO, 1x, saleable, buyable
        #     - Garden Table Top : 1x, not saleable, not buyable
        #     - Garden Table Leg : 4x, not saleable, not buyable
        # Ordering Garden Furniture should create a PO for the Garden Table
        product = self.product_garden_furniture
        purchase_orders_before = self.purchase_order_model.search([])
        order = self.create_sale_order(product)
        order.action_confirm()
        purchase_orders_after = self.purchase_order_model.search(
            [("id", "not in", purchase_orders_before.ids)]
        )
        self.assertTrue(purchase_orders_after)

        purchase_lines = purchase_orders_after.order_line
        # There should be 2 lines in the PO
        self.assertEqual(len(purchase_lines), 2.0)
        # Table is MTO, we should have a line for it, qty = 5.0
        table_line = purchase_lines.filtered(
            lambda l: l.product_id == self.product_garden_table
        )
        self.assertTrue(table_line)
        self.assertEqual(table_line.product_qty, 5.0)
        # Chair is MTO, we should have a line for it, with qty = 20.0
        chair_line = purchase_lines.filtered(
            lambda l: l.product_id == self.product_garden_chair
        )
        self.assertTrue(chair_line)
        self.assertEqual(chair_line.product_qty, 20.0)
