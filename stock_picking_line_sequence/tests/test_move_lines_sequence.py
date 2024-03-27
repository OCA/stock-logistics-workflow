# Copyright 2017 Camptocamp SA - Damien Crier, Alexandre Fayolle
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import Form, common


class TestStockMove(common.TransactionCase):
    def setUp(self):
        super().setUp()
        # Useful models
        self.Picking = self.env["stock.picking"]
        self.product_id_1 = self.env.ref("product.product_product_8")
        self.product_id_2 = self.env.ref("product.product_product_11")
        self.product_id_3 = self.env.ref("product.product_product_6")
        self.picking_type_in = self.env.ref("stock.warehouse0").in_type_id
        self.supplier_location = self.env.ref("stock.stock_location_suppliers")
        self.customer_location = self.env.ref("stock.stock_location_customers")

    def _create_picking(self):
        """Create a Picking."""
        picking = self.Picking.create(
            {
                "picking_type_id": self.picking_type_in.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.customer_location.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "move 1",
                            "product_id": self.product_id_1.id,
                            "product_uom_qty": 5.0,
                            "product_uom": self.product_id_1.uom_id.id,
                            "location_id": self.supplier_location.id,
                            "location_dest_id": self.customer_location.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "move 2",
                            "product_id": self.product_id_2.id,
                            "product_uom_qty": 5.0,
                            "product_uom": self.product_id_2.uom_id.id,
                            "location_id": self.supplier_location.id,
                            "location_dest_id": self.customer_location.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "move 3",
                            "product_id": self.product_id_3.id,
                            "product_uom_qty": 5.0,
                            "product_uom": self.product_id_3.uom_id.id,
                            "location_id": self.supplier_location.id,
                            "location_dest_id": self.customer_location.id,
                        },
                    ),
                ],
            }
        )
        return picking

    def test_move_lines_sequence(self):
        self.picking = self._create_picking()
        self.picking._compute_max_line_sequence()
        self.picking.move_ids.write({"product_uom_qty": 10.0})
        self.picking2 = self.picking.copy()
        self.assertEqual(
            self.picking2[0].move_ids[0].sequence,
            self.picking.move_ids[0].sequence,
            "The Sequence is not copied properly",
        )
        self.assertEqual(
            self.picking2[0].move_ids[1].sequence,
            self.picking.move_ids[1].sequence,
            "The Sequence is not copied properly",
        )
        self.assertEqual(
            self.picking2[0].move_ids[2].sequence,
            self.picking.move_ids[2].sequence,
            "The Sequence is not copied properly",
        )
        picking_form = Form(self.picking)
        with picking_form.move_ids_without_package.new() as move_form:
            move_form.product_id = self.product_id_1
            self.assertEqual(move_form.sequence, self.picking.max_line_sequence)

    def test_backorder(self):
        picking = self._create_picking()
        picking._compute_max_line_sequence()
        picking.action_confirm()
        picking.action_assign()
        picking.move_line_ids[0].write({"quantity": 3})
        picking.move_line_ids[2].write({"quantity": 3})
        res_dict = picking.button_validate()
        self.assertEqual(res_dict["res_model"], "stock.backorder.confirmation")
        backorder_wiz = (
            self.env["stock.backorder.confirmation"]
            .browse(res_dict.get("res_id"))
            .with_context(**res_dict["context"])
        )
        backorder_wiz.process()
        picking_backorder = self.Picking.search([("backorder_id", "=", picking.id)])
        self.assertEqual(
            picking_backorder[0].move_ids[1].sequence, 3, "Backorder wrong sequence"
        )
        self.assertEqual(
            picking_backorder[0].move_ids[0].sequence, 1, "Backorder wrong sequence"
        )

    def test_move_lines_aggregated(self):
        picking = self._create_picking()
        picking._compute_max_line_sequence()
        picking.action_confirm()
        agg_mls = picking.move_line_ids[0]._get_aggregated_product_quantities()
        for key in agg_mls:
            self.assertNotEqual(
                agg_mls[key].get("sequence2", "NA"),
                "NA",
                "The field sequence2 is not added in dictionary",
            )
            self.assertEqual(
                picking.move_line_ids[0].move_id.sequence2,
                agg_mls[key]["sequence2"],
                "The Sequence is not copied properly in " "the aggregated move lines",
            )
