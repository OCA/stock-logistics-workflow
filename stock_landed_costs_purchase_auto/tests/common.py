# Copyright 2021-2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.tests import Form, common, new_test_user


class TestPurchaseOrderBase(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Remove this variable in v16 and put instead:
        # from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT
        DISABLED_MAIL_CONTEXT = {
            "tracking_disable": True,
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.company = cls.env.ref("base.main_company")
        cls.category = cls.env["product.category"].create(
            {"name": "Test category", "property_cost_method": "average"}
        )
        cls.product_storable = cls.env["product.product"].create(
            {
                "name": "Producto Storable",
                "type": "product",
                "categ_id": cls.category.id,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Mr Odoo"})
        cls.company.lc_journal_id = cls.env["account.journal"].create(
            {
                "name": "Test LC",
                "type": "general",
                "code": "MISC-LC",
                "company_id": cls.company.id,
            }
        )
        cls.purchase_user = new_test_user(
            cls.env, login="test_purchase_user", groups="purchase.group_purchase_user"
        )
        cls.order = cls._create_purchase_order(cls)

    def _create_purchase_order(self):
        order_form = Form(self.env["purchase.order"])
        order_form.partner_id = self.partner
        with order_form.order_line.new() as line_form:
            line_form.product_id = self.product_storable
        order = order_form.save()
        return order

    def _action_picking_validate(self, picking):
        res = picking.button_validate()
        model = self.env[res["res_model"]].with_context(**res["context"])
        model.create({}).process()
