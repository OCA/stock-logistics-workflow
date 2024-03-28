# Copyright 2024 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.stock_account.tests.test_stockvaluation import TestStockValuation


class TestStockOwnerValued(TestStockValuation):
    @classmethod
    def setUpClass(cls):
        super(TestStockOwnerValued, cls).setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "product",
                "categ_id": cls.env.ref("product.product_category_all").id,
                "standard_price": 100.00,
            }
        )
        cls.product.categ_id.property_valuation = "real_time"
        cls.owner2 = cls.env["res.partner"].create(
            {
                "name": "Owner 2",
                "value_owner_inventory": True,
            }
        )

    def _create_picking(self, owner):
        picking = self.env["stock.picking"].create(
            {
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "partner_id": self.partner.id,
                "picking_type_id": self.env.ref("stock.picking_type_in").id,
                "owner_id": owner.id,
            }
        )
        move = self.env["stock.move"].create(
            {
                "picking_id": picking.id,
                "name": "10 in",
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "product_id": self.product.id,
                "product_uom": self.uom_unit.id,
                "product_uom_qty": 10.0,
                "price_unit": 10,
            }
        )
        picking.action_confirm()
        picking.action_assign()
        move.move_line_ids.qty_done = 10
        picking._action_done()
        return picking

    def test_stock_account_owner_valued(self):
        # Create picking with owner1
        picking = self._create_picking(self.owner1)
        move = picking.move_ids
        # Picking with owner1 should not create valuation
        self.assertEqual(move.restrict_partner_id.id, self.owner1.id)
        self.assertFalse(move.stock_valuation_layer_ids)

        # Create Picking with owner2
        picking = self._create_picking(self.owner2)
        move = picking.move_ids
        # picking with owner2 should create valuation
        self.assertEqual(move.restrict_partner_id.id, self.owner2.id)
        self.assertTrue(move.stock_valuation_layer_ids)
        self.assertTrue(bool(move.stock_valuation_layer_ids.account_move_id))
