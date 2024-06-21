# Copyright 2020 Iryna Vyshnevska Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class StockPickingReturnLotTest(common.SavepointCase):
    def setUp(self):
        super().setUp()
        self.picking_obj = self.env["stock.picking"]
        partner = self.env["res.partner"].create({"name": "Test"})
        product = self.env["product.product"].create(
            {"name": "test_product", "type": "product", "tracking": "serial"}
        )
        lot_1 = self.env["stock.production.lot"].create(
            {"name": "000001", "product_id": product.id}
        )
        lot_2 = self.env["stock.production.lot"].create(
            {"name": "000002", "product_id": product.id}
        )
        picking_type_out = self.env.ref("stock.picking_type_out")
        stock_location = self.env.ref("stock.stock_location_stock")
        customer_location = self.env.ref("stock.stock_location_customers")
        self.env["stock.quant"]._update_available_quantity(
            product, stock_location, 1, lot_id=lot_1
        )
        self.env["stock.quant"]._update_available_quantity(
            product, stock_location, 1, lot_id=lot_2
        )
        self.picking = self.picking_obj.create(
            {
                "partner_id": partner.id,
                "picking_type_id": picking_type_out.id,
                "location_id": stock_location.id,
                "location_dest_id": customer_location.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "product_uom_qty": 2,
                            "product_uom": product.uom_id.id,
                            "location_id": stock_location.id,
                            "location_dest_id": customer_location.id,
                        },
                    )
                ],
            }
        )
        self.picking.move_lines[0].write(
            {
                "move_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "qty_done": 1.0,
                            "lot_id": lot_1.id,
                            "product_uom_id": product.uom_id.id,
                            "location_id": stock_location.id,
                            "location_dest_id": customer_location.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "qty_done": 1.0,
                            "lot_id": lot_2.id,
                            "product_uom_id": product.uom_id.id,
                            "location_id": stock_location.id,
                            "location_dest_id": customer_location.id,
                            "picking_id": self.picking.id,
                        },
                    ),
                ]
            }
        )
        self.picking.action_confirm()
        self.picking.action_assign()
        self.picking.move_lines._action_done()

    def create_return_wiz(self):
        return (
            self.env["stock.return.picking"]
            .with_context(active_id=self.picking.id, active_model="stock.picking")
            .create({})
        )

    def test_return(self):
        wiz = self.create_return_wiz()
        wiz._onchange_picking_id()
        self.assertEqual(len(wiz.product_return_moves), 1)
        picking_returned_id = wiz._create_returns()[0]
        picking_returned = self.picking_obj.browse(picking_returned_id)

        self.assertEqual(len(picking_returned.move_line_ids), 2)
        self.assertTrue(
            picking_returned.move_line_ids.filtered(lambda l: l.lot_id.name == "000002")
        )
        self.assertTrue(
            picking_returned.move_line_ids.filtered(lambda l: l.lot_id.name == "000001")
        )
