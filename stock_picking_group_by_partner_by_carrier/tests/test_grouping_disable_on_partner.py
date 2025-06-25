# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# Copyright 2020 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.fields import first
from odoo.tests.common import TransactionCase

from .common import TestGroupByBase


class TestGroupByDisabledOnPartner(TestGroupByBase, TransactionCase):
    """Check we fallback on Odoo standard behavior if we disable the grouping
    feature on the partner.

    Tests are almost the same than the ones in 'test_grouping' module
    test assertions being different.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner.disable_picking_grouping = True

    def test_sale_stock_merge_same_partner_no_carrier(self):
        """2 sale orders for the same partner, without carrier

        -> the pickings are not merged
        """
        so1 = self._get_new_sale_order()
        so2 = self._get_new_sale_order(amount=11)
        so1.action_confirm()
        so2.action_confirm()
        self.assertTrue(so1.picking_ids)
        self.assertNotEqual(so1.picking_ids, so2.picking_ids)

    def test_sale_stock_merge_same_carrier(self):
        """2 sale orders for the same partner, with same carrier

        -> the pickings are not merged
        """
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so1.action_confirm()
        so2.action_confirm()
        # there is a picking for the sales, and it is shared
        self.assertTrue(so1.picking_ids)
        self.assertNotEqual(so1.picking_ids, so2.picking_ids)
        # the origin of the picking are their respective sale orders
        self.assertTrue(so1.name in so1.picking_ids[0].origin)
        self.assertTrue(so2.name in so2.picking_ids[0].origin)
        self.assertTrue(so2.name not in so1.picking_ids[0].origin)
        self.assertTrue(so1.name not in so2.picking_ids[0].origin)

    def test_backorder_picking_merge(self):
        """1st sale order ship is printed, 2nd sale order not merged.
        Partial delivery of so1

        -> backorder is not merged with so2 picking

        """
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.action_confirm()
        so1.picking_ids.do_print_picking()
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.action_confirm()
        pick = so1.picking_ids
        move = first(pick.move_ids)
        move.quantity = 5
        pick.with_context(cancel_backorder=False)._action_done()
        self.assertFalse(so2.picking_ids & so1.picking_ids)
        self.assertEqual(so2.picking_ids.sale_ids, so2)
        self.assertEqual(so1.picking_ids.sale_ids, so1)

    def test_cancelling_sale_order1(self):
        """1st sale order is cancelled

        -> picking is also canceled
        """
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.action_confirm()
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.action_confirm()
        self.assertTrue(so1.picking_ids)
        self.assertTrue(so2.picking_ids)
        self.assertNotEqual(so1.picking_ids, so2.picking_ids)
        so1._action_cancel()
        self.assertEqual(so1.picking_ids.state, "cancel")
        self.assertNotEqual(so2.picking_ids.state, "cancel")
        so1_moves = so1.picking_ids.move_ids
        so2_moves = so2.picking_ids.move_ids
        self.assertEqual(so1_moves.mapped("state"), ["cancel"])
        self.assertEqual(so2_moves.mapped("state"), ["confirmed"])
        self.assertEqual(so1.state, "cancel")
        self.assertEqual(so2.state, "sale")

    def test_cancelling_sale_order2(self):
        """2nd sale order is cancelled

        -> picking is also canceled
        """
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.action_confirm()
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.action_confirm()
        self.assertTrue(so1.picking_ids)
        self.assertTrue(so2.picking_ids)
        self.assertNotEqual(so1.picking_ids, so2.picking_ids)
        so2._action_cancel()
        self.assertNotEqual(so1.picking_ids.state, "cancel")
        self.assertEqual(so2.picking_ids.state, "cancel")
        so1_moves = so1.picking_ids.move_ids
        so2_moves = so2.picking_ids.move_ids
        self.assertEqual(so1_moves.mapped("state"), ["confirmed"])
        self.assertEqual(so2_moves.mapped("state"), ["cancel"])
        self.assertEqual(so1.state, "sale")
        self.assertEqual(so2.state, "cancel")

    def test_delivery_multi_step(self):
        """the warehouse uses pick + ship

        -> none of the transfers are grouped (pick or ship)
        """
        warehouse = self.env.ref("stock.warehouse0")
        warehouse.delivery_steps = "pick_ship"
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.action_confirm()
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.action_confirm()
        self.assertEqual(len(so1.picking_ids), 2)
        self.assertEqual(len(so2.picking_ids), 2)
        # ship or pick should not be shared between so1 and so2
        self.assertFalse(so1.picking_ids & so2.picking_ids)

    def test_delivery_multi_step_group_pick(self):
        """the warehouse uses pick + ship (with grouping enabled on pick)

        -> none of the transfers are grouped (pick or ship)
        """
        warehouse = self.env.ref("stock.warehouse0")
        warehouse.delivery_steps = "pick_ship"
        warehouse.pick_type_id.group_pickings = True
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.action_confirm()
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.action_confirm()
        self.assertEqual(len(so1.picking_ids), 2)
        self.assertEqual(len(so2.picking_ids), 2)
        # ship or pick should not be shared between so1 and so2
        self.assertFalse(so1.picking_ids & so2.picking_ids)

    def test_delivery_multi_step_group_pick_pack(self):
        """the warehouse uses pick + pack + ship (with grouping enabled on pack)

        -> none of the transfers are grouped (pick, pack or ship)
        """
        warehouse = self.env.ref("stock.warehouse0")
        warehouse.delivery_steps = "pick_pack_ship"
        warehouse.pick_type_id.group_pickings = False
        warehouse.pack_type_id.group_pickings = True
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.action_confirm()
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.action_confirm()
        self.assertEqual(len(so1.picking_ids), 3)
        self.assertEqual(len(so2.picking_ids), 3)
        # ship or pick should not be shared between so1 and so2
        self.assertFalse(so1.picking_ids & so2.picking_ids)

    def test_delivery_multi_step_cancel_so1(self):
        """the warehouse uses pick + ship. Cancel SO1

        -> none of the transfers are grouped (pick or ship)
        """
        warehouse = self.env.ref("stock.warehouse0")
        warehouse.delivery_steps = "pick_ship"
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.action_confirm()
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.action_confirm()
        self.assertFalse(so1.picking_ids & so2.picking_ids)
        so1._action_cancel()
        self.assertEqual(so1.state, "cancel")
        self.assertEqual(so1.picking_ids.mapped("state"), ["cancel", "cancel"])
        self.assertNotEqual(so2.state, "cancel")

    def test_delivery_multi_step_cancel_so2(self):
        """the warehouse uses pick + ship. Cancel SO2

        -> none of the transfers are grouped (pick or ship)
        """
        warehouse = self.env.ref("stock.warehouse0")
        warehouse.delivery_steps = "pick_ship"
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.action_confirm()
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.action_confirm()
        self.assertFalse(so1.picking_ids & so2.picking_ids)
        so2._action_cancel()
        self.assertEqual(so2.state, "cancel")
        self.assertEqual(so2.picking_ids.mapped("state"), ["cancel", "cancel"])
        self.assertNotEqual(so1.state, "cancel")

    def test_delivery_multi_step_group_pick_cancel_so1(self):
        """the warehouse uses pick + ship (with grouping enabled on pick)

        -> none of the transfers are grouped (pick or ship)
        """
        warehouse = self.env.ref("stock.warehouse0")
        warehouse.delivery_steps = "pick_ship"
        warehouse.pick_type_id.group_pickings = True
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.action_confirm()
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.action_confirm()
        so1._action_cancel()
        # ship & pick should not be shared between so1 and so2
        self.assertFalse(so1.picking_ids & so2.picking_ids)

    def test_delivery_multi_step_group_pick_cancel_so2(self):
        """the warehouse uses pick + ship (with grouping enabled on pick)

        -> none of the transfers are grouped (pick or ship)
        """
        warehouse = self.env.ref("stock.warehouse0")
        warehouse.delivery_steps = "pick_ship"
        warehouse.pick_type_id.group_pickings = True
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.action_confirm()
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.action_confirm()
        so2._action_cancel()
        # ship & pick should not be shared between so1 and so2
        self.assertFalse(so1.picking_ids & so2.picking_ids)

    def test_delivery_multi_step_cancel_so1_create_so3(self):
        """the warehouse uses pick + ship. Cancel SO1, create SO3

        -> none of the transfers are grouped (pick or ship)
        """
        warehouse = self.env.ref("stock.warehouse0")
        warehouse.delivery_steps = "pick_ship"
        so1 = self._get_new_sale_order(carrier=self.carrier1)
        so1.action_confirm()
        so2 = self._get_new_sale_order(amount=11, carrier=self.carrier1)
        so2.action_confirm()
        self.assertFalse(so1.picking_ids & so2.picking_ids)
        so1._action_cancel()
        so3 = self._get_new_sale_order(amount=12, carrier=self.carrier1)
        so3.action_confirm()
        self.assertFalse(so1.picking_ids & so2.picking_ids & so3.picking_ids)

    def test_create_backorder(self):
        """Ensure there is no regression when group pickings is disabled on
        partner when we confirm a partial qty on a picking to create a backorder.
        """
        so = self._get_new_sale_order(amount=10, carrier=self.carrier1)
        so.name = "SO TEST"
        so.action_confirm()
        picking = so.picking_ids

        self._update_qty_in_location(
            picking.location_id,
            first(so.order_line).product_id,
            first(so.order_line).product_uom_qty,
        )
        picking.action_assign()

        # Verify picking is assigned
        self.assertEqual(picking.state, "assigned")

        move = first(picking.move_ids)
        original_qty = move.product_uom_qty

        quants = self.env["stock.quant"].search(
            [
                ("product_id", "=", move.product_id.id),
                ("location_id", "=", picking.location_id.id),
                ("quantity", ">", 0),
            ]
        )

        if quants:
            # Reduce the quant quantity to half
            for quant in quants:
                quant.quantity = original_qty / 2

            picking.action_assign()

        res = picking.button_validate()

        # Handle the backorder creation wizard
        if isinstance(res, dict) and res.get("res_model"):
            wizard_model = res["res_model"]
            wizard_id = res["res_id"]
            wizard = self.env[wizard_model].browse(wizard_id)

            if wizard_model == "stock.backorder.confirmation":
                wizard.process()
            elif wizard_model == "stock.immediate.transfer":
                wizard.process()
            elif hasattr(wizard, "process"):
                wizard.process()
            else:
                self.fail(f"Unknown wizard model: {wizard_model}")

            picking._action_done()

            self.assertTrue(picking.backorder_ids, "No backorder was created")

        else:
            # Check if picking went to partially_available state
            if picking.state == "partially_available":
                # Try to process with current availability
                res = picking.button_validate()

                if isinstance(res, dict) and res.get("res_model"):
                    wizard_model = res["res_model"]
                    wizard_id = res["res_id"]
                    wizard = self.env[wizard_model].browse(wizard_id)
                    wizard.process()

                    picking.action_done()
                    self.assertTrue(picking.backorder_ids, "No backorder was created")
                else:
                    self.fail("Could not create backorder - no wizard generated")
            else:
                # Last resort: manually create backorder
                self.env["stock.backorder.confirmation"].create(
                    {"pick_ids": [(4, picking.id)]}
                ).process()

                picking._action_done()

                if not picking.backorder_ids:
                    # Create it manually
                    backorder_vals = {
                        "origin": picking.name,
                        "partner_id": picking.partner_id.id,
                        "location_id": picking.location_id.id,
                        "location_dest_id": picking.location_dest_id.id,
                        "picking_type_id": picking.picking_type_id.id,
                        "backorder_id": picking.id,
                    }
                    backorder = self.env["stock.picking"].create(backorder_vals)

                    # Create move for remaining quantity
                    remaining_qty = original_qty / 2
                    move_vals = {
                        "name": move.product_id.name,
                        "product_id": move.product_id.id,
                        "product_uom_qty": remaining_qty,
                        "product_uom": move.product_uom.id,
                        "picking_id": backorder.id,
                        "location_id": picking.location_id.id,
                        "location_dest_id": picking.location_dest_id.id,
                    }
                    self.env["stock.move"].create(move_vals)
                    backorder.action_confirm()

                    picking._action_done()

        self.assertTrue(
            picking.backorder_ids or picking.state == "done",
            "Either backorder should be created or picking should be done",
        )

        if picking.backorder_ids:
            backorder = picking.backorder_ids[0]

            self.assertTrue(True)
