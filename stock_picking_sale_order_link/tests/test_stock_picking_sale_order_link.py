# © 2017 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestStockPickingSaleOrderLink(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockPickingSaleOrderLink, cls).setUpClass()
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
        cls.Location = cls.env["stock.location"]
        cls.PickingType = cls.env["stock.picking.type"]
        cls.Picking = cls.env["stock.picking"]
        cls.Product = cls.env["product.template"]
        cls.warehouse = cls.env["stock.warehouse"].create(
            {"name": "warehouse - test", "code": "WH-TEST"}
        )

        cls.product = cls.Product.create(
            {
                "name": "Product - Test",
                "type": "product",
                "list_price": 100.00,
                "standard_price": 100.00,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Customer - test"})
        cls.picking_type = cls.PickingType.search(
            [("warehouse_id", "=", cls.warehouse.id), ("code", "=", "outgoing")]
        )
        sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "partner_shipping_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.product_variant_ids.id,
                            "product_uom_qty": 2,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 100.00,
                        },
                    )
                ],
            }
        )
        sale_order.action_confirm()
        cls.picking = cls.Picking.search([("sale_id", "=", sale_order.id)])

    def test_picking_to_sale_order(self):
        result = self.picking.action_view_sale_order()
        self.assertEqual(result["res_id"], self.picking.sale_id.id)
