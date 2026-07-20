# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.stock.tests.common import TestStockCommon


@tagged("post_install", "-at_install")
class TestStockReturnForceUnpack(TestStockCommon):
    def _enable_force_unpack(self, source_picking_type):
        """Enable the flag on every operation type a return/exchange of
        ``source_picking_type`` can resolve to.

        `stock.warehouse` wires `return_picking_type_id` both ways (out <->
        in) on creation, so a return's resolved operation type is not
        `source_picking_type` itself but its configured return type.
        """
        return_type = source_picking_type.return_picking_type_id or source_picking_type
        return_type.force_unpack_on_return = True
        return_of_return_type = return_type.return_picking_type_id or return_type
        return_of_return_type.force_unpack_on_return = True

    def _deliver_and_pack(self, qty):
        self.env["stock.quant"]._update_available_quantity(
            self.productA, self.stock_location, qty
        )
        picking = self.PickingObj.create(
            {
                "picking_type_id": self.picking_type_out.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
            }
        )
        self.MoveObj.create(
            {
                "product_id": self.productA.id,
                "product_uom_qty": qty,
                "product_uom": self.uom_unit.id,
                "picking_id": picking.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
            }
        )
        picking.action_confirm()
        picking.action_assign()
        picking.move_ids.move_line_ids.quantity = qty
        picking.action_put_in_pack()
        picking.move_ids.picked = True
        picking.button_validate()
        return picking

    def _create_return(self, picking, qty):
        return_wizard = (
            self.env["stock.return.picking"]
            .with_context(
                active_id=picking.id,
                active_ids=picking.ids,
                active_model="stock.picking",
            )
            .create({})
        )
        return_wizard.product_return_moves.quantity = qty
        res = return_wizard.action_create_returns()
        return self.PickingObj.browse(res["res_id"])

    def test_partial_return_keeps_source_package_by_default(self):
        """Without the flag, a partial return of a packed delivery keeps a
        reference to the original "Put in pack" package as its source
        package, even though most of it is still held at the customer."""
        picking = self._deliver_and_pack(100)
        return_picking = self._create_return(picking, 50)

        self.assertEqual(
            return_picking.move_line_ids.package_id,
            picking.move_line_ids.result_package_id,
        )

    def test_partial_return_succeeds_with_force_unpack(self):
        self._enable_force_unpack(self.picking_type_out)
        picking = self._deliver_and_pack(100)
        return_picking = self._create_return(picking, 50)

        self.assertEqual(
            return_picking.move_line_ids.package_id,
            picking.move_line_ids.result_package_id,
        )
        self.assertFalse(return_picking.move_line_ids.result_package_id)

        return_picking.move_ids.move_line_ids.quantity = 50
        return_picking.move_ids.picked = True
        return_picking.button_validate()

    def test_force_unpack_keeps_nested_source_package(self):
        """The destination is cleared even when the source package is
        nested under a parent container; the source itself is preserved
        so the nested quant is still resolved correctly."""
        self._enable_force_unpack(self.picking_type_out)
        picking = self._deliver_and_pack(100)
        original_package = picking.move_line_ids.result_package_id
        parent_package = self.env["stock.package"].create({"name": "PARENT-PACK"})
        original_package.parent_package_id = parent_package

        return_picking = self._create_return(picking, 50)

        self.assertEqual(return_picking.move_line_ids.package_id, original_package)
        self.assertFalse(return_picking.move_line_ids.result_package_id)

    def test_exchange_respects_force_unpack(self):
        """`_create_exchange()` is only used for incoming pickings; outgoing
        exchanges are generated through procurement instead, so this
        exercises the receipt/exchange-to-supplier path."""
        self._enable_force_unpack(self.picking_type_in)
        picking = self.PickingObj.create(
            {
                "picking_type_id": self.picking_type_in.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        self.MoveObj.create(
            {
                "product_id": self.productA.id,
                "product_uom_qty": 100,
                "product_uom": self.uom_unit.id,
                "picking_id": picking.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
            }
        )
        picking.action_confirm()
        picking.action_assign()
        picking.move_ids.move_line_ids.quantity = 100
        picking.action_put_in_pack()
        picking.move_ids.picked = True
        picking.button_validate()

        return_wizard = (
            self.env["stock.return.picking"]
            .with_context(
                active_id=picking.id,
                active_ids=picking.ids,
                active_model="stock.picking",
            )
            .create({})
        )
        return_wizard.product_return_moves.quantity = 50
        action = return_wizard.action_create_exchanges()
        return_picking = self.PickingObj.browse(action["res_id"])
        exchange_picking = self.PickingObj.search(
            [("return_id", "=", return_picking.id)]
        )

        self.assertTrue(return_picking.move_line_ids.package_id)
        self.assertFalse(return_picking.move_line_ids.result_package_id)
        self.assertTrue(exchange_picking)
        self.assertFalse(exchange_picking.move_line_ids.result_package_id)
