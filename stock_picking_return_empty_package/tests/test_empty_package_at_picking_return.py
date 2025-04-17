# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import Form, TransactionCase


class TestEmptyPackageAtPickingReturn(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Product 1", "type": "product"}
        )
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.loc_stock = cls.warehouse.lot_stock_id
        cls.loc_customer = cls.env.ref("stock.stock_location_customers")
        cls.pick_type = cls.env.ref("stock.picking_type_out")
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.loc_stock, 10
        )
        cls.picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.pick_type.id,
                "location_id": cls.loc_stock.id,
                "location_dest_id": cls.loc_customer.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": "Test move 1a",
                            "product_id": cls.product.id,
                            "product_uom": cls.product.uom_id.id,
                            "product_uom_qty": 10,
                            "location_id": cls.loc_stock.id,
                            "location_dest_id": cls.loc_customer.id,
                        }
                    )
                ],
            }
        )
        cls.picking.action_confirm()
        cls.picking.action_assign()
        cls.picking.action_set_quantities_to_reservation()
        cls.picking._put_in_pack(cls.picking.move_line_ids)
        cls.picking._action_done()

    @classmethod
    def _return_picking(cls, picking, quantity):
        stock_form = Form(
            cls.env["stock.return.picking"].with_context(
                active_ids=picking.ids,
                active_id=picking.id,
                active_model="stock.picking",
            )
        )
        wizard = stock_form.save()
        wizard.product_return_moves.write({"quantity": quantity})
        res = wizard.create_returns()
        return cls.env["stock.picking"].browse(res["res_id"])

    def test_00(self):
        self.pick_type.empty_package_at_return = False
        # Quants in stock before
        quant_before = self.product.stock_quant_ids.filtered(
            lambda q, loc=self.loc_stock: q.location_id == loc
        )
        return_picking = self._return_picking(self.picking, 10)
        self.assertTrue(return_picking.move_line_ids.result_package_id)
        return_picking.action_set_quantities_to_reservation()
        return_picking._action_done()
        quant = (
            self.product.stock_quant_ids.filtered(
                lambda q, loc=self.loc_stock: q.location_id == loc
            )
            - quant_before
        )
        self.assertEqual(len(quant), 1)
        self.assertTrue(quant.package_id)

    def test_01(self):
        self.pick_type.empty_package_at_return = True
        return_picking = self._return_picking(self.picking, 10)
        self.assertFalse(return_picking.move_line_ids.result_package_id)
        return_picking.action_set_quantities_to_reservation()
        return_picking._action_done()
        quant = self.product.stock_quant_ids.filtered(
            lambda q, loc=self.loc_stock: q.location_id == loc
        )
        self.assertEqual(len(quant), 1)
        self.assertFalse(quant.package_id)
