# Copyright 2024 Tecnativa - Sergio Teruel
# Copyright 2024 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class TestStockPickingBatchOutgoing(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["res.config.settings"].write(
            {
                "group_stock_adv_location": True,
                "group_stock_multi_locations": True,
            }
        )
        # Picking Types
        cls.picking_type_internal = cls.env.ref("stock.picking_type_internal")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        # Stock Locations
        cls.stock_loc = cls.env.ref("stock.stock_location_stock")
        cls.stock_loc_output = cls.env.ref("stock.stock_location_output")
        cls.customer_loc = cls.env.ref("stock.stock_location_customers")

        cls.partner = cls.env["res.partner"].create({"name": "Partner test"})
        cls.product = cls.env["product.product"].create(
            {"name": "product_product_test", "type": "product"}
        )

        # Create a product route containing a stock rule that will
        # generate a move from Stock for every procurement created in Output
        product_route = cls.env["stock.location.route"].create(
            {
                "name": "Stock -> output route",
                "product_selectable": True,
                "rule_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Stock -> output rule",
                            "action": "pull",
                            "picking_type_id": cls.picking_type_internal.id,
                            "location_src_id": cls.stock_loc.id,
                            "location_id": cls.stock_loc_output.id,
                        },
                    )
                ],
            }
        )
        # Set this route on `product.product_product_3`
        cls.product.write({"route_ids": [(4, product_route.id)]})
        # Create Delivery Order of 10 `product.product_product_3` from Output -> Customer
        vals = {
            "name": "Delivery order for procurement",
            "partner_id": cls.partner.id,
            "picking_type_id": cls.picking_type_out.id,
            "location_id": cls.stock_loc_output.id,
            "location_dest_id": cls.customer_loc.id,
            "move_lines": [
                (
                    0,
                    0,
                    {
                        "name": "/",
                        "product_id": cls.product.id,
                        "product_uom": cls.product.uom_id.id,
                        "product_uom_qty": 10.00,
                        "procure_method": "make_to_order",
                        "location_id": cls.stock_loc_output.id,
                        "location_dest_id": cls.customer_loc.id,
                    },
                )
            ],
        }
        cls.pick_output = cls.env["stock.picking"].create(vals)
        cls.pick_output.move_lines._onchange_product_id()

        # Confirm delivery order.
        cls.pick_output.action_confirm()

        # I run the scheduler.
        # Note: If purchase if already installed, the method _run_buy will be called due
        # to the purchase demo data. As we update the stock module to run this test, the
        # method won't be an attribute of stock.procurement at this moment. For that reason
        # we mute the logger when running the scheduler.
        with mute_logger("odoo.addons.stock.models.procurement"):
            cls.env["procurement.group"].run_scheduler()

    def test_batch_picking_outgoing(self):
        # Check that a picking was created from stock to output.
        moves = self.env["stock.move"].search(
            [
                ("product_id", "=", self.product.id),
                ("location_id", "=", self.stock_loc.id),
                ("location_dest_id", "=", self.stock_loc_output.id),
                ("move_dest_ids", "in", self.pick_output.move_lines[0].ids),
            ]
        )
        self.assertEqual(
            len(moves.ids),
            1,
            "It should have created a picking from Stock to Output with the original"
            "picking as destination",
        )
        wizard = self.env["stock.picking.to.batch"].create({"mode": "new"})
        wizard.with_context(active_ids=self.pick_output.id).attach_pickings()
        self.assertTrue(moves.picking_id.batch_outgoing_id)
        self.assertNotEqual(moves.picking_id, self.pick_output)
        # Do a backorder
        self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": self.stock_loc.id,
                "quantity": 50,
            }
        )
        picking = moves.picking_id
        picking.move_lines.quantity_done = 5
        picking.with_context(cancel_backorder=False)._action_done()
        self.assertTrue(picking.backorder_ids.batch_outgoing_id)
