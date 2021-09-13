# Copyright 2015 Guewen Baconnier
# Copyright 2016 Lorenzo Battistini - Agile Business Group
# Copyright 2016 Alessio Gerace - Agile Business Group
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.exceptions import UserError
from odoo.tests import Form, common


class TestPackagePreparation(common.SavepointCase):
    def _create_picking(self, product, product_extra=None, quantity=5.0):
        picking_form = Form(self.env["stock.picking"])
        picking_form.partner_id = self.partner
        picking_form.picking_type_id = self.env.ref("stock.picking_type_out")
        with picking_form.move_ids_without_package.new() as line_form:
            line_form.product_id = product
        if product_extra:
            with picking_form.move_ids_without_package.new() as line_form:
                line_form.product_id = product_extra
        picking = picking_form.save()
        picking.move_ids_without_package.write({"product_uom_qty": quantity})
        return picking

    def _create_preparation(self, pickings):
        return self.env["stock.picking.package.preparation"].create(
            {
                "partner_id": self.partner.id,
                "picking_ids": [(6, 0, pickings.ids)],
                "packaging_id": self.packaging.id,
            }
        )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("base.res_partner_2")
        cls.product1 = cls.env.ref("product.product_product_16")
        cls.product2 = cls.env.ref("product.product_product_13")
        cls.product3 = cls.env.ref("product.product_product_20")
        packaging_prod = cls.env["product.product"].create({"name": "Pallet"})
        cls.packaging = cls.env["product.packaging"].create(
            {"name": "Pallet", "product_id": packaging_prod.id}
        )
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.cust_location = cls.env.ref("stock.stock_location_customers")

        cls.env["stock.quant"]._update_available_quantity(
            cls.product1, cls.stock_location, 10.0
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product2, cls.stock_location, 5.0
        )

        cls.picking_a = cls._create_picking(cls, cls.product1, cls.product2)
        cls.picking_b = cls._create_picking(cls, cls.product1)

    def test_put_in_pack(self):
        pickings = self.picking_a + self.picking_b
        pickings.action_assign()

        prep = self._create_preparation(pickings)
        prep.action_put_in_pack()
        self.assertTrue(prep.package_id)
        self.assertEqual(
            pickings.mapped("move_line_ids.result_package_id"),
            prep.package_id,
            "All the moves should have a stock.quant.operation with "
            "the same result package",
        )

    def test_put_in_pack_keep_done_qty(self):
        pickings = self.picking_a + self.picking_b
        move_lines = pickings.mapped("move_line_ids")

        move_lines.write({"qty_done": 1})
        pickings.action_assign()

        prep = self._create_preparation(pickings)
        prep.action_put_in_pack()
        for move in move_lines:
            self.assertEqual(move.qty_done, 1)

    def test_done(self):
        pickings = self.picking_a + self.picking_b
        pickings.action_assign()

        prep = self._create_preparation(pickings)
        prep.action_put_in_pack()

        prep.action_done()

        self.assertTrue(all(picking.state == "done" for picking in pickings))
        self.assertEqual(
            prep.quant_ids.mapped("location_id").id,
            self.env.ref("stock.stock_location_customers").id,
        )
        self.assertEqual(
            prep.quant_ids.mapped("product_id"), self.product2 | self.product1
        )
        for quant in prep.quant_ids:
            if quant.product_id.id == self.product1.id:
                self.assertEqual(quant.quantity, 10)
            if quant.product_id.id == self.product2.id:
                self.assertEqual(quant.quantity, 5)

    def test_pack_values(self):
        pickings = self.picking_a + self.picking_b
        pickings.action_assign()
        prep = self._create_preparation(pickings)
        prep.action_put_in_pack()
        package = prep.package_id
        self.assertEqual(package.packaging_id, self.packaging)

    def test_weight(self):
        location = self.env.ref("stock.stock_location_customers")
        self.product1.weight = 5  # * 5 units
        self.product2.weight = 2  # * 5 units
        pickings = self.picking_a + self.picking_b
        pickings.action_assign()
        prep = self._create_preparation(pickings)
        prep.action_put_in_pack()
        prep.action_done()
        self.assertEqual(prep.weight, 60.0)
        self.assertEqual(prep.package_id.location_id, location)

    def test_cancel_draft(self):
        pickings = self.picking_a + self.picking_b
        pickings.action_assign()

        prep = self._create_preparation(pickings)
        prep.action_put_in_pack()
        prep.action_cancel()

        self.assertTrue(all(p.state == "cancel" for p in prep))
        self.assertTrue(all(not p.package_id for p in prep))

        prep.action_draft()
        prep.action_put_in_pack()
        prep.action_done()

        with self.assertRaises(UserError):
            prep.action_cancel()
