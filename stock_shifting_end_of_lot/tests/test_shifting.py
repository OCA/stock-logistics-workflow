# © 2020 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import SavepointCase


class Test(SavepointCase):
    def setUp(self):
        super().setUp()
        conf = self.env["res.config.settings"].create(
            {
                "group_stock_multi_warehouses": True,
                "group_stock_multi_locations": True,
            }
        )
        conf.execute()
        vals = {
            "end_lot_location_id": self.ref("end_lot_location").id,
            "end_lot_picking_type_id": self.env.ref("stock.picking_type_internal").id,
        }
        self.env.ref("stock.picking_type_out").write(vals)
        inventory = self.ref("inventory_move_end_lot")
        inventory.action_validate()
        assert inventory.state == "done"
        assert self.ref("product_4_end_lot1").qty_available == 100
        picking = self.ref("picking_out_end_lot_product")
        assert picking.state == "draft"
        picking.action_confirm()
        assert picking.state == "confirmed"
        picking.action_assign()
        assert picking.state == "assigned"
        assert len(picking.move_lines) == 3
        self.picking = picking

    def test_end_lot(self):
        pick = self.picking
        assert len(pick.move_line_ids.mapped("lot_id")) == 2
        self.validate_picking(pick)
        assert pick.state == "done"
        # search end_of_lot picking generated when validated pick
        end_lot = self.env["stock.picking"].search(
            [("origin", "ilike", "End of lot from%")], limit=1
        )
        assert len(end_lot.move_lines) == 3
        end_lot.action_confirm()
        end_lot.action_assign()
        assert end_lot.state == "assigned"
        self.validate_picking(end_lot)
        # Check that quantity are the rest of the stock
        self.check_qty("product_4_end_lot1", end_lot, 10)
        assert self.ref("product_4_end_lot1").qty_available == 0
        self.check_qty("product_4_end_lot2", end_lot, 10)
        self.check_qty("product_4_end_lot_no_lot", end_lot, 5)
        assert self.ref("product_4_end_lot1").qty_available == 0

    def validate_picking(self, picking):
        action = picking.button_validate()
        assert len(picking.move_lines) == 3
        wizard = self.env[(action.get("res_model"))].browse(action.get("res_id"))
        wizard.process()

    def check_qty(self, xml_id, picking, qty):
        assert (
            picking.move_lines.filtered(
                lambda s: s.product_id == self.ref(xml_id)
            ).quantity_done
            == qty
        )

    def ref(self, xml_id):
        "shortcut for a local xml"
        return self.env.ref("stock_shifting_end_of_lot.%s" % xml_id)
