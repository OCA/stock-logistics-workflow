# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form, TransactionCase


class TestStockValuationFifoCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        product_category = cls.env["product.category"].create(
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
                "categ_id": product_category.id,
                "tracking": "lot",
            }
        )
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")

    def create_picking(
        self,
        location,
        location_dest,
        picking_type,
        lot_numbers,
        price_unit=0.0,
        is_receipt=True,
        force_lot_name=None,
    ):
        picking = self.env["stock.picking"].create(
            {
                "location_id": location.id,
                "location_dest_id": location_dest.id,
                "picking_type_id": picking_type.id,
            }
        )
        move_line_qty = 5.0
        move = self.env["stock.move"].create(
            {
                "name": "Test",
                "product_id": self.product.id,
                "location_id": picking.location_id.id,
                "location_dest_id": picking.location_dest_id.id,
                "product_uom": self.product.uom_id.id,
                "product_uom_qty": move_line_qty * len(lot_numbers),
                "picking_id": picking.id,
            }
        )
        if price_unit:
            move.write({"price_unit": price_unit})

        for lot in lot_numbers:
            move_line = self.env["stock.move.line"].create(
                {
                    "move_id": move.id,
                    "picking_id": picking.id,
                    "product_id": self.product.id,
                    "location_id": move.location_id.id,
                    "location_dest_id": move.location_dest_id.id,
                    "product_uom_id": move.product_uom.id,
                    "qty_done": move_line_qty,
                }
            )
            if is_receipt:
                move_line.lot_name = lot
            else:
                lot = self.env["stock.lot"].search(
                    [("product_id", "=", self.product.id), ("name", "=", lot)], limit=1
                )
                move_line.lot_id = lot.id
                if force_lot_name:
                    force_lot = self.env["stock.lot"].search(
                        [
                            ("product_id", "=", self.product.id),
                            ("name", "=", force_lot_name),
                        ],
                        limit=1,
                    )
                    move_line.force_fifo_lot_id = force_lot.id
        picking.action_confirm()
        picking.action_assign()
        picking._action_done()
        return picking, move

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
