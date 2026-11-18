# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form, TransactionCase


class TestStockValuationFifoCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        product_categ = cls.env["product.category"].create(
            {
                "name": "Test Category",
                "property_cost_method": "fifo",
                "property_valuation": "real_time",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "product",
                "categ_id": product_categ.id,
                "tracking": "lot",
            }
        )
        cls.vendor_loc = cls.env.ref("stock.stock_location_suppliers")
        cls.cust_loc = cls.env.ref("stock.stock_location_customers")
        cls.stock_loc = cls.env.ref("stock.stock_location_stock")
        cls.pick_type_in = cls.env.ref("stock.picking_type_in")
        cls.pick_type_out = cls.env.ref("stock.picking_type_out")

    def create_picking(
        self, op_type, lot_numbers, ml_qty=5.0, price=0.0, force_lot_name=None
    ):
        loc = self.vendor_loc
        loc_dest = self.stock_loc
        pick_type = self.pick_type_in
        if op_type == "out":
            loc = self.stock_loc
            loc_dest = self.cust_loc
            pick_type = self.pick_type_out
        pick = self.env["stock.picking"].create(
            {
                "location_id": loc.id,
                "location_dest_id": loc_dest.id,
                "picking_type_id": pick_type.id,
            }
        )
        move = self.env["stock.move"].create(
            {
                "name": "Test",
                "product_id": self.product.id,
                "location_id": loc.id,
                "location_dest_id": loc_dest.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": ml_qty * len(lot_numbers),
                "picking_id": pick.id,
                "price_unit": price,
            }
        )
        for lot in lot_numbers:
            move_line = self.env["stock.move.line"].create(
                {
                    "move_id": move.id,
                    "picking_id": pick.id,
                    "product_id": self.product.id,
                    "location_id": loc.id,
                    "location_dest_id": loc_dest.id,
                    "product_uom_id": move.product_uom.id,
                    "qty_done": ml_qty,
                }
            )
            if op_type == "in":
                move_line.lot_name = lot
                continue
            move_line.lot_id = self.env["stock.lot"].search(
                [("product_id", "=", self.product.id), ("name", "=", lot)], limit=1
            )
            if not force_lot_name:
                continue
            force_lot = self.env["stock.lot"].search(
                [("product_id", "=", self.product.id), ("name", "=", force_lot_name)],
                limit=1,
            )
            move_line.force_fifo_lot_id = force_lot.id
        pick.action_confirm()
        pick.action_assign()
        pick._action_done()
        return pick, move

    def transfer_return(self, original_picking, return_qty):
        return_picking_wizard_form = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=original_picking.ids,
                active_id=original_picking.id,
                active_model="stock.picking",
            )
        )
        return_picking_wizard = return_picking_wizard_form.save()
        return_picking_wizard.product_return_moves.write({"quantity": return_qty})
        return_picking_wizard_action = return_picking_wizard.create_returns()
        return_picking = self.env["stock.picking"].browse(
            return_picking_wizard_action["res_id"]
        )
        return_move = return_picking.move_ids
        return_move.move_line_ids.qty_done = return_qty
        return_picking.button_validate()
        return return_move
