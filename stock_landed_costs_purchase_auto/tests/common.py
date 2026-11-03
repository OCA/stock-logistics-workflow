# Copyright 2021-2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.tests import Form, new_test_user

from odoo.addons.base.tests.common import BaseCommon


class TestPurchaseOrderBase(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")
        cls.category = cls.env["product.category"].create(
            {"name": "Test category", "property_cost_method": "average"}
        )
        cls.product_storable = cls.env["product.product"].create(
            {
                "name": "Producto Storable",
                "type": "consu",
                "categ_id": cls.category.id,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Mr Odoo"})
        cls.purchase_user = new_test_user(
            cls.env,
            login="test_purchase_user",
            groups="purchase.group_purchase_user,stock.group_stock_user",
        )
        cls.order = cls._create_purchase_order(cls)

    def _create_purchase_order(self):
        order_form = Form(self.env["purchase.order"])
        order_form.partner_id = self.partner
        with order_form.order_line.new() as line_form:
            line_form.product_id = self.product_storable
        order = order_form.save()
        return order

    def _create_dropship_picking(self):
        suppliers = self.env.ref("stock.stock_location_suppliers")
        customers = self.env.ref("stock.stock_location_customers")
        return self.env["stock.picking"].create(
            {
                "picking_type_id": self.env.ref("stock.picking_type_in").id,
                "partner_id": self.partner.id,
                "location_id": suppliers.id,
                "location_dest_id": customers.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_storable.id,
                            "product_uom_qty": 1.0,
                            "location_id": suppliers.id,
                            "location_dest_id": customers.id,
                        },
                    )
                ],
            }
        )

    def _action_picking_validate(self, picking):
        if any(move.state == "confirmed" for move in picking.move_ids):
            picking.action_assign()
        for move in picking.move_ids:
            move.quantity = move.product_uom_qty if not move.quantity else move.quantity
        res = picking.button_validate()
        if (
            isinstance(res, dict)
            and res.get("res_model") == "stock.backorder.confirmation"
        ):
            wizard = Form(
                self.env[res["res_model"]].with_context(**res["context"])
            ).save()
            wizard.process()
        return res
