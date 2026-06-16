# Copyright 2017 Camptocamp SA - Damien Crier, Alexandre Fayolle
# Copyright 2017 ForgeFlow, S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import Form, common


class TestStockMove(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Useful models
        cls.Picking = cls.env["stock.picking"]
        cls.category_office = cls.env["product.category"].create(
            {
                "name": "Office Furniture",
            }
        )

        cls.uom_unit = cls.env.ref("uom.product_uom_unit")

        cls.product_large_desk = cls.env["product.product"].create(
            {
                "name": "Large Desk",
                "categ_id": cls.category_office.id,
                "standard_price": 1299.0,
                "list_price": 1799.0,
                "type": "consu",
                "uom_id": cls.uom_unit.id,
                "default_code": "E-COM09",
            }
        )

        cls.product_conference_chair = cls.env["product.product"].create(
            {
                "name": "Conference Chair",
                "categ_id": cls.category_office.id,
                "standard_price": 28.0,
                "list_price": 33.0,
                "type": "consu",
                "uom_id": cls.uom_unit.id,
                "default_code": "E-COM12",
            }
        )

        cls.product_large_cabinet = cls.env["product.product"].create(
            {
                "name": "Large Cabinet",
                "categ_id": cls.category_office.id,
                "standard_price": 800.0,
                "list_price": 320.0,
                "type": "consu",
                "uom_id": cls.uom_unit.id,
                "default_code": "E-COM07",
            }
        )

        cls.main_partner = cls.env.ref("base.main_partner")

        cls.warehouse0 = cls.env["stock.warehouse"].create(
            {
                "name": "Test Warehouse",
                "code": "TWH",
                "partner_id": cls.main_partner.id,
                "company_id": cls.env.company.id,
            }
        )

        cls.picking_type_in = cls.warehouse0.in_type_id

        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")

    def _create_picking(cls):
        """Create a Picking."""
        picking = cls.Picking.create(
            {
                "picking_type_id": cls.picking_type_in.id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.customer_location.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_large_desk.id,
                            "product_uom_qty": 5.0,
                            "product_uom": cls.product_large_desk.uom_id.id,
                            "location_id": cls.supplier_location.id,
                            "location_dest_id": cls.customer_location.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_conference_chair.id,
                            "product_uom_qty": 5.0,
                            "product_uom": cls.product_conference_chair.uom_id.id,
                            "location_id": cls.supplier_location.id,
                            "location_dest_id": cls.customer_location.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_large_cabinet.id,
                            "product_uom_qty": 5.0,
                            "product_uom": cls.product_large_cabinet.uom_id.id,
                            "location_id": cls.supplier_location.id,
                            "location_dest_id": cls.customer_location.id,
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
            self.picking2.move_ids[0].sequence,
            self.picking.move_ids[0].sequence,
            "The Sequence is not copied properly",
        )
        self.assertEqual(
            self.picking2.move_ids[1].sequence,
            self.picking.move_ids[1].sequence,
            "The Sequence is not copied properly",
        )
        self.assertEqual(
            self.picking2.move_ids[2].sequence,
            self.picking.move_ids[2].sequence,
            "The Sequence is not copied properly",
        )
        picking_form = Form(self.picking)
        with picking_form.move_ids.new() as move_form:
            move_form.product_id = self.product_large_desk
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

    def test_split(self):
        picking = self._create_picking()
        picking._compute_max_line_sequence()
        picking.action_confirm()
        picking.action_assign()
        picking_product_sequence_map = {
            move.product_id.id: move.sequence for move in picking.move_ids
        }
        picking.move_line_ids[0].write({"quantity": 3})
        picking.move_line_ids[2].write({"quantity": 3})
        picking.action_split_transfer()
        picking_backorder = picking.backorder_ids
        for move in picking_backorder.move_ids:
            self.assertEqual(
                move.sequence, picking_product_sequence_map.get(move.product_id.id)
            )

    def test_move_lines_aggregated(self):
        picking = self._create_picking()
        picking._compute_max_line_sequence()
        picking.action_confirm()
        agg_mls = picking.move_line_ids[0]._get_aggregated_product_quantities()
        for key in agg_mls:
            self.assertNotEqual(
                agg_mls[key].get("visible_sequence", "NA"),
                "NA",
                "The field visible_sequence is not added in dictionary",
            )
            self.assertEqual(
                picking.move_line_ids[0].move_id.visible_sequence,
                agg_mls[key]["visible_sequence"],
                "The Sequence is not copied properly in the aggregated move lines",
            )
