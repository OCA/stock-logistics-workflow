# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo.tests.common import Form


class TestQuickPicking(TransactionCase):
    def setUp(self):
        super(TestQuickPicking, self).setUp()
        # Useful models
        self.Picking = self.env["stock.picking"]
        self.location_id = self.env.ref(
            "stock.warehouse0"
        ).wh_output_stock_loc_id
        self.dest_loc = self.env.ref("stock.stock_location_customers")
        self.product_id_1 = self.env.ref("product.product_product_8")
        self.product_id_2 = self.env.ref("product.product_product_11")
        picking_vals = {
            "location_id": self.location_id.id,
            "location_dest_id": self.dest_loc.id,
            "picking_type_id": self.ref("stock.picking_type_out"),
        }
        self.picking = self.Picking.create(picking_vals)
        with Form(self.picking, "stock.view_picking_form") as picking_form:
            picking_form.location_id = self.location_id
        self.default_cont = {
            "parent_id": self.picking.id,
            "parent_model": "stock.picking",
        }

    def test_quick_picking(self):
        # test add stock.move
        self.product_id_1.with_context(self.default_cont).qty_to_process = 5.0
        self.assertEqual(
            len(self.picking.move_ids_without_package),
            1,
            "Picking: no stock.move created",
        )
        self.product_id_2.with_context(self.default_cont).qty_to_process = 6.0
        self.assertEqual(
            len(self.picking.move_ids_without_package),
            2,
            "Stock move count must be 2",
        )
        # test stock move qty
        for line in self.picking.move_ids_without_package:
            if line.product_id == self.product_id_1:
                self.assertEqual(line.product_qty, 5)
            if line.product_id == self.product_id_2:
                self.assertEqual(line.product_qty, 6)

        # test update stock.move qty
        self.product_id_1.with_context(self.default_cont).qty_to_process = 3.0
        self.product_id_2.with_context(self.default_cont).qty_to_process = 2.0
        self.assertEqual(
            len(self.picking.move_ids_without_package),
            2,
            "Stock move count must be 2",
        )
        # test stock move qty after update
        for line in self.picking.move_ids_without_package:
            if line.product_id == self.product_id_1:
                self.assertEqual(line.product_qty, 3)
            if line.product_id == self.product_id_2:
                self.assertEqual(line.product_qty, 2)

    def test_add_product_action_opened(self):
        product_act_from_picking = self.picking.add_product()
        self.assertEqual(
            product_act_from_picking["type"], "ir.actions.act_window"
        )
        self.assertEqual(
            product_act_from_picking["res_model"], "product.product"
        )
        self.assertEqual(product_act_from_picking["view_mode"], "tree")
        self.assertEqual(product_act_from_picking["target"], "current")
        self.assertEqual(
            product_act_from_picking["view_id"][0],
            self.env.ref("stock_picking_quick.product_tree_view4picking").id,
        )
        self.assertEqual(
            product_act_from_picking["context"]["parent_id"], self.picking.id
        )
