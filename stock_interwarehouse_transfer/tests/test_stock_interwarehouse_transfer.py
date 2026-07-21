# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form, tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestStockInterwarehouseTransfer(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")
        if not cls.company.internal_transit_location_id:
            cls.company.internal_transit_location_id = cls.env["stock.location"].create(
                {
                    "name": "Internal Transit",
                    "usage": "transit",
                    "company_id": cls.company.id,
                }
            )
        cls.wh_a = cls.env["stock.warehouse"].create(
            {"name": "Warehouse A", "code": "WHA"}
        )
        cls.wh_b = cls.env["stock.warehouse"].create(
            {"name": "Warehouse B", "code": "WHB"}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "type": "product"}
        )
        cls.product_b = cls.env["product.product"].create(
            {"name": "Test Product B", "type": "product"}
        )
        cls.env["stock.quant"].create(
            [
                {
                    "product_id": product.id,
                    "location_id": cls.wh_a.lot_stock_id.id,
                    "quantity": 100.0,
                }
                for product in cls.product | cls.product_b
            ]
        )

    @classmethod
    def _create_transfer(cls, qty=10.0, lines=None):
        lines = lines or [(cls.product, qty)]
        return cls.env["stock.interwarehouse.transfer"].create(
            {
                "warehouse_from_id": cls.wh_a.id,
                "warehouse_to_id": cls.wh_b.id,
                "line_ids": [
                    fields.Command.create(
                        {
                            "product_id": product.id,
                            "product_uom_qty": line_qty,
                        }
                    )
                    for product, line_qty in lines
                ],
            }
        )

    @classmethod
    def _stage_pickings(cls, transfer, stage):
        return transfer.picking_ids.filtered(lambda p: p.picking_type_id.code == stage)

    @classmethod
    def _stage_moves(cls, line, stage):
        """Every move of `line` in `stage`, cancelled ones included."""
        return line.move_ids.filtered(lambda m: m.picking_type_id.code == stage)

    @classmethod
    def _validate_picking(cls, picking, qty=None):
        """Validate `picking`, for a partial `qty` when given (creates a backorder)."""
        for move in picking.move_ids:
            move.quantity_done = move.product_uom_qty if qty is None else qty
        res = picking.button_validate()
        if (
            isinstance(res, dict)
            and res.get("res_model") == "stock.backorder.confirmation"
        ):
            Form(
                cls.env[res["res_model"]].with_context(**res["context"])
            ).save().process()
        return picking

    def test_01_ensure_op_types_creates_out_and_in(self):
        self.wh_a._ensure_inter_wh_op_types()
        self.assertTrue(self.wh_a.out_inter_wh_type_id)
        self.assertTrue(self.wh_a.in_inter_wh_type_id)
        self.assertEqual(self.wh_a.out_inter_wh_type_id.code, "outgoing")
        self.assertEqual(self.wh_a.in_inter_wh_type_id.code, "incoming")
        transit = self.company.internal_transit_location_id
        self.assertEqual(
            self.wh_a.out_inter_wh_type_id.default_location_dest_id, transit
        )
        self.assertEqual(self.wh_a.in_inter_wh_type_id.default_location_src_id, transit)

    def test_02_ensure_op_types_idempotent(self):
        self.wh_a._ensure_inter_wh_op_types()
        out_type_id = self.wh_a.out_inter_wh_type_id.id
        self.wh_a._ensure_inter_wh_op_types()
        self.assertEqual(self.wh_a.out_inter_wh_type_id.id, out_type_id)

    def test_03_line_default_uom(self):
        transfer = self.env["stock.interwarehouse.transfer"].create(
            {
                "warehouse_from_id": self.wh_a.id,
                "warehouse_to_id": self.wh_b.id,
            }
        )
        line = self.env["stock.interwarehouse.transfer.line"].create(
            {
                "transfer_id": transfer.id,
                "product_id": self.product.id,
                "product_uom_qty": 5.0,
            }
        )
        self.assertEqual(line.product_uom, self.product.uom_id)

    def test_04_header_default_locations(self):
        transfer = self.env["stock.interwarehouse.transfer"].create(
            {
                "warehouse_from_id": self.wh_a.id,
                "warehouse_to_id": self.wh_b.id,
            }
        )
        self.assertEqual(transfer.location_id, self.wh_a.lot_stock_id)
        self.assertEqual(transfer.location_dest_id, self.wh_b.lot_stock_id)

    def test_05_same_company_constraint(self):
        other_company = self.env["res.company"].create({"name": "Other Company"})
        wh_other = (
            self.env["stock.warehouse"]
            .with_context(allowed_company_ids=[other_company.id])
            .create(
                {
                    "name": "Other WH",
                    "code": "OWH",
                    "company_id": other_company.id,
                }
            )
        )
        with self.assertRaises(ValidationError):
            self.env["stock.interwarehouse.transfer"].create(
                {
                    "warehouse_from_id": self.wh_a.id,
                    "warehouse_to_id": wh_other.id,
                }
            )

    def test_06_same_warehouse_constraint(self):
        with self.assertRaises(ValidationError):
            self.env["stock.interwarehouse.transfer"].create(
                {
                    "warehouse_from_id": self.wh_a.id,
                    "warehouse_to_id": self.wh_a.id,
                }
            )

    def test_07_initial_state_is_draft(self):
        transfer = self.env["stock.interwarehouse.transfer"].create(
            {
                "warehouse_from_id": self.wh_a.id,
                "warehouse_to_id": self.wh_b.id,
            }
        )
        self.assertEqual(transfer.state, "draft")

    def test_08_confirm_creates_two_pickings(self):
        transfer = self._create_transfer()
        transfer.action_confirm()
        self.assertEqual(len(transfer.picking_ids), 2)
        transit = self.company.internal_transit_location_id
        out = transfer.picking_ids.filtered(
            lambda p: p.picking_type_id.code == "outgoing"
        )
        in_ = transfer.picking_ids.filtered(
            lambda p: p.picking_type_id.code == "incoming"
        )
        self.assertEqual(out.location_dest_id, transit)
        self.assertEqual(in_.location_id, transit)
        self.assertEqual(out.picking_type_id, self.wh_a.out_inter_wh_type_id)
        self.assertEqual(in_.picking_type_id, self.wh_b.in_inter_wh_type_id)

    def test_09_confirm_moves_are_linked(self):
        transfer = self._create_transfer(qty=7.0)
        transfer.action_confirm()
        out = transfer.picking_ids.filtered(
            lambda p: p.picking_type_id.code == "outgoing"
        )
        in_ = transfer.picking_ids.filtered(
            lambda p: p.picking_type_id.code == "incoming"
        )
        out_move = out.move_ids
        in_move = in_.move_ids
        self.assertEqual(len(out_move), 1)
        self.assertEqual(len(in_move), 1)
        self.assertIn(out_move, in_move.move_orig_ids)
        self.assertEqual(out_move.product_uom_qty, 7.0)
        self.assertEqual(in_move.product_uom_qty, 7.0)
        line = transfer.line_ids
        self.assertEqual(out_move.interwh_transfer_line_id, line)
        self.assertEqual(in_move.interwh_transfer_line_id, line)
        self.assertEqual(line.move_ids, out_move | in_move)

    def test_10_confirm_state_becomes_confirmed(self):
        transfer = self._create_transfer()
        transfer.action_confirm()
        self.assertEqual(transfer.state, "confirmed")

    def test_11_state_in_transit_after_out_validated(self):
        transfer = self._create_transfer()
        transfer.action_confirm()
        out = transfer.picking_ids.filtered(
            lambda p: p.picking_type_id.code == "outgoing"
        )
        out.move_ids.quantity_done = 10.0
        out.button_validate()
        self.assertEqual(transfer.state, "in_transit")

    def test_12_state_done_after_in_validated(self):
        transfer = self._create_transfer()
        transfer.action_confirm()
        out = transfer.picking_ids.filtered(
            lambda p: p.picking_type_id.code == "outgoing"
        )
        out.move_ids.quantity_done = 10.0
        out.button_validate()
        in_ = transfer.picking_ids.filtered(
            lambda p: p.picking_type_id.code == "incoming"
        )
        in_.move_ids.quantity_done = 10.0
        in_.button_validate()
        self.assertEqual(transfer.state, "done")

    def test_13_cancel_sets_state_cancelled(self):
        transfer = self._create_transfer()
        transfer.action_confirm()
        transfer.action_cancel()
        self.assertEqual(transfer.state, "cancelled")
        self.assertTrue(all(p.state == "cancel" for p in transfer.picking_ids))

    def test_14_name_has_sequence_prefix(self):
        transfer = self._create_transfer()
        transfer.action_confirm()
        self.assertTrue(transfer.name.startswith("IWT/"))

    def test_15_backorder_linked_to_transfer(self):
        transfer = self._create_transfer(qty=10.0)
        transfer.action_confirm()
        out = self._stage_pickings(transfer, "outgoing")
        self._validate_picking(out, qty=5.0)
        backorders = out.backorder_ids
        self.assertTrue(backorders)
        for bo in backorders:
            self.assertEqual(bo.interwarehouse_transfer_id, transfer)

    def test_16_custom_header_locations_on_moves(self):
        custom_src = self.env["stock.location"].create(
            {
                "name": "Custom Shelf A",
                "location_id": self.wh_a.lot_stock_id.id,
                "usage": "internal",
            }
        )
        custom_dest = self.env["stock.location"].create(
            {
                "name": "Custom Shelf B",
                "location_id": self.wh_b.lot_stock_id.id,
                "usage": "internal",
            }
        )
        self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": custom_src.id,
                "quantity": 50.0,
            }
        )
        transfer = self.env["stock.interwarehouse.transfer"].create(
            {
                "warehouse_from_id": self.wh_a.id,
                "warehouse_to_id": self.wh_b.id,
                "location_id": custom_src.id,
                "location_dest_id": custom_dest.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 5.0,
                        },
                    )
                ],
            }
        )
        transfer.action_confirm()
        out = transfer.picking_ids.filtered(
            lambda p: p.picking_type_id.code == "outgoing"
        )
        in_ = transfer.picking_ids.filtered(
            lambda p: p.picking_type_id.code == "incoming"
        )
        self.assertEqual(out.move_ids.location_id, custom_src)
        self.assertEqual(in_.move_ids.location_dest_id, custom_dest)

    def test_17_internal_move_across_warehouses_blocked(self):
        with self.assertRaises(ValidationError):
            self.env["stock.move"].create(
                {
                    "name": self.product.name,
                    "product_id": self.product.id,
                    "product_uom": self.product.uom_id.id,
                    "product_uom_qty": 1.0,
                    "picking_type_id": self.wh_a.int_type_id.id,
                    "location_id": self.wh_a.lot_stock_id.id,
                    "location_dest_id": self.wh_b.lot_stock_id.id,
                }
            )

    def test_18_internal_move_same_warehouse_allowed(self):
        sublocation = self.env["stock.location"].create(
            {
                "name": "Shelf A",
                "location_id": self.wh_a.lot_stock_id.id,
                "usage": "internal",
            }
        )
        move = self.env["stock.move"].create(
            {
                "name": self.product.name,
                "product_id": self.product.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": 1.0,
                "picking_type_id": self.wh_a.int_type_id.id,
                "location_id": self.wh_a.lot_stock_id.id,
                "location_dest_id": sublocation.id,
            }
        )
        self.assertTrue(move)

    def test_19_decrease_qty_on_confirmed(self):
        transfer = self._create_transfer(qty=10.0)
        transfer.action_confirm()
        line = transfer.line_ids
        line.product_uom_qty = 4.0
        self.assertEqual(len(transfer.picking_ids), 2)
        for stage in ("outgoing", "incoming"):
            moves = self._stage_moves(line, stage)
            self.assertEqual(len(moves), 1, stage)
            self.assertEqual(moves.product_uom_qty, 4.0, stage)

    def test_20_decrease_qty_to_zero_cancels_moves(self):
        transfer = self._create_transfer(qty=10.0)
        transfer.action_confirm()
        line = transfer.line_ids
        moves = line.move_ids
        line.product_uom_qty = 0.0
        self.assertTrue(moves)
        self.assertTrue(all(m.state == "cancel" for m in moves))

    def test_21_increase_qty_on_confirmed(self):
        transfer = self._create_transfer(qty=10.0)
        transfer.action_confirm()
        line = transfer.line_ids
        line.product_uom_qty = 15.0
        self.assertEqual(len(transfer.picking_ids), 2)
        for stage in ("outgoing", "incoming"):
            moves = self._stage_moves(line, stage)
            self.assertEqual(len(moves), 1, stage)
            self.assertEqual(moves.product_uom_qty, 15.0, stage)

    def test_22_same_product_lines_keep_distinct_moves(self):
        transfer = self._create_transfer(
            lines=[(self.product, 4.0), (self.product, 6.0)]
        )
        transfer.action_confirm()
        first_line, second_line = transfer.line_ids
        for stage in ("outgoing", "incoming"):
            first_move = self._stage_moves(first_line, stage)
            second_move = self._stage_moves(second_line, stage)
            self.assertEqual(len(first_move), 1, stage)
            self.assertEqual(len(second_move), 1, stage)
            self.assertNotEqual(first_move, second_move, stage)
            self.assertEqual(first_move.product_uom_qty, 4.0, stage)
            self.assertEqual(second_move.product_uom_qty, 6.0, stage)

    def test_23_add_line_on_confirmed(self):
        transfer = self._create_transfer(qty=10.0)
        transfer.action_confirm()
        line = self.env["stock.interwarehouse.transfer.line"].create(
            {
                "transfer_id": transfer.id,
                "product_id": self.product_b.id,
                "product_uom_qty": 3.0,
            }
        )
        self.assertEqual(len(transfer.picking_ids), 2)
        out_move = self._stage_moves(line, "outgoing")
        in_move = self._stage_moves(line, "incoming")
        self.assertEqual(out_move.product_uom_qty, 3.0)
        self.assertEqual(in_move.product_uom_qty, 3.0)
        self.assertEqual(
            out_move.picking_id, self._stage_pickings(transfer, "outgoing")
        )
        self.assertIn(out_move, in_move.move_orig_ids)

    def test_24_remove_line_on_confirmed(self):
        transfer = self._create_transfer(
            lines=[(self.product, 10.0), (self.product_b, 3.0)]
        )
        transfer.action_confirm()
        kept_line, removed_line = transfer.line_ids
        kept_moves = kept_line.move_ids
        removed_moves = removed_line.move_ids
        removed_line.unlink()
        self.assertTrue(removed_moves)
        self.assertTrue(all(m.state == "cancel" for m in removed_moves))
        self.assertTrue(all(m.state != "cancel" for m in kept_moves))

    def test_25_decrease_below_done_qty_blocked(self):
        transfer = self._create_transfer(qty=10.0)
        transfer.action_confirm()
        line = transfer.line_ids
        self._validate_picking(self._stage_pickings(transfer, "outgoing"), qty=5.0)
        self.assertEqual(line.qty_shipped, 5.0)
        backorder_move = self._stage_moves(line, "outgoing").filtered(
            lambda m: m.state not in ("done", "cancel")
        )
        self.assertEqual(backorder_move.interwh_transfer_line_id, line)
        with self.assertRaises(UserError), self.cr.savepoint():
            line.product_uom_qty = 3.0
        line.product_uom_qty = 5.0
        self.assertEqual(line._get_stage_qty("outgoing"), 5.0)

    def test_26_increase_qty_while_in_transit(self):
        transfer = self._create_transfer(qty=10.0)
        transfer.action_confirm()
        line = transfer.line_ids
        out_picking = self._stage_pickings(transfer, "outgoing")
        self._validate_picking(out_picking)
        self.assertEqual(transfer.state, "in_transit")
        line.product_uom_qty = 12.0
        out_pickings = self._stage_pickings(transfer, "outgoing")
        self.assertEqual(len(out_pickings), 2)
        new_out_picking = out_pickings - out_picking
        self.assertEqual(new_out_picking.interwarehouse_transfer_id, transfer)
        self.assertEqual(new_out_picking.group_id, transfer.procurement_group_id)
        self.assertEqual(new_out_picking.move_ids.product_uom_qty, 2.0)
        in_move = self._stage_moves(line, "incoming")
        self.assertEqual(in_move.product_uom_qty, 12.0)
        self.assertIn(new_out_picking.move_ids, in_move.move_orig_ids)
