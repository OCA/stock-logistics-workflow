# Copyright 2023 Ooops404
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestRestrictLotUpdate(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer_loc = cls.env.ref("stock.stock_location_customers")
        cls.output_loc = cls.env.ref("stock.stock_location_output")
        cls.product = cls.env.ref("product.product_product_16")
        cls.product.write({"tracking": "lot"})
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.write({"delivery_steps": "pick_ship"})
        cls.lot = cls.env["stock.production.lot"].create(
            {
                "name": "lot1",
                "product_id": cls.product.id,
                "company_id": cls.warehouse.company_id.id,
            }
        )

    def test_restrict_lot_change_propagation(self):
        """
        Check that changes to the lot restriction field propagate
        from a move to its linked moves - but only forwards towards
        move_dest_ids, not backwards
        """
        # make warehouse output in two step
        self.env["res.config.settings"].write(
            {
                "group_stock_adv_location": True,
                "group_stock_multi_locations": True,
            }
        )
        self.product.categ_id.route_ids |= self.env["stock.location.route"].search(
            [("name", "ilike", "deliver in 2")]
        )
        lot2 = self.env["stock.production.lot"].create(
            {
                "name": "lot 2",
                "product_id": self.product.id,
                "company_id": self.warehouse.company_id.id,
            }
        )

        procurement_group = self.env["procurement.group"].create(
            {"name": "My procurement", "move_type": "one"}
        )
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    self.product,
                    15,
                    self.product.uom_id,
                    self.customer_loc,
                    "a name",
                    "an origin restrict on lot 1",
                    self.env.company,
                    {
                        "group_id": procurement_group,
                        "restrict_lot_id": self.lot.id,
                    },
                ),
                self.env["procurement.group"].Procurement(
                    self.product,
                    30,
                    self.product.uom_id,
                    self.customer_loc,
                    "a name",
                    "no origin restrict",
                    self.env.company,
                    {
                        "group_id": procurement_group,
                    },
                ),
            ]
        )
        picking_after, picking_before = self.env["stock.picking"].search(
            [("group_id", "=", procurement_group.id)]
        )
        (
            move_before_restrict,
            move_before_no_restrict,
        ) = picking_before.move_ids_without_package
        (
            move_after_restrict,
            move_after_no_restrict,
        ) = picking_after.move_ids_without_package

        self.assertEqual(move_before_restrict.restrict_lot_id, self.lot)
        self.assertEqual(move_after_restrict.restrict_lot_id, self.lot)
        self.assertFalse(move_before_no_restrict.restrict_lot_id)
        self.assertFalse(move_after_no_restrict.restrict_lot_id)

        move_before_restrict.restrict_lot_id = lot2
        self.assertEqual(
            move_after_restrict.restrict_lot_id, lot2, msg="Lot Restriction didn't sync"
        )

        move_after_restrict.restrict_lot_id = self.lot
        self.assertEqual(
            move_before_restrict.restrict_lot_id,
            lot2,
            msg="Lot Restriction shouldn't sync backwards",
        )

        move_before_no_restrict.restrict_lot_id = lot2
        self.assertEqual(
            move_after_no_restrict.restrict_lot_id,
            lot2,
            msg="Lot Restriction didn't sync",
        )
        move_before_no_restrict.restrict_lot_id = False
        self.assertFalse(
            move_after_no_restrict.restrict_lot_id, msg="Lot Restriction didn't sync"
        )

    def test_enforce_lot_domain(self):
        """
        Test that the setting applies correctly and lot restriction
        is only applied to products within the domain of the setting
        """
        company = self.env.company
        self.assertEqual(company.enforce_lot_restriction_product_domain, "[]")

        move = self.env["stock.move"].create(
            {
                "product_id": self.product.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "location_dest_id": self.customer_loc.id,
                "product_uom_qty": 1,
                "product_uom": self.product.uom_id.id,
                "name": "test",
                "warehouse_id": self.warehouse.id,
                "restrict_lot_id": self.lot.id,
            }
        )
        self.assertFalse(move.change_restrict_lot)

        company.enforce_lot_restriction_product_domain = (
            "[('id', '!=', %s)]" % self.product.id
        )

        move._compute_change_restrict_lot()
        self.assertTrue(move.change_restrict_lot)
