# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import Form


class TestCommonSale:
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.WizardQty = cls.env["stock.change.product.qty"]

        cls.Partner = cls.env["res.partner"]
        cls.Product = cls.env["product.product"]
        cls.SaleOrder = cls.env["sale.order"]
        cls.SaleOrderLine = cls.env["sale.order.line"]

        cls.partner = cls.Partner.create({"name": "Customer"})

        cls.array_products = [
            {
                "product": cls.Product.create(
                    {"name": "Test Product 1", "type": "product"}
                ),
                "product_uom_qty": 10,
                "qty_delivered": 0,
            },
            {
                "product": cls.Product.create(
                    {"name": "Test Product 2", "type": "product"}
                ),
                "product_uom_qty": 10,
                "qty_delivered": 0,
            },
            {
                "product": cls.Product.create(
                    {"name": "Test Product 3", "type": "product"}
                ),
                "product_uom_qty": 10,
                "qty_delivered": 0,
            },
        ]

        cls.service_product = cls.Product.create(
            {"name": "Test Product service", "type": "service"}
        )

        cls.so_empty = cls.create_basic_so([])
        cls.so_one_line = cls.create_basic_so(cls.array_products[:1])
        cls.so_three_line = cls.create_basic_so(cls.array_products)

        cls.so_with_service_line = cls.create_basic_so(
            cls.array_products[:1]
            + [
                {
                    "product": cls.service_product,
                    "product_uom_qty": 10,
                    "qty_delivered": 0,
                }
            ]
        )

    @classmethod
    def _update_stock(cls, product, qty):
        """
        Set the stock quantity of the product
        :param product: product.product recordset
        :param qty: float
        """
        wizard = Form(cls.WizardQty)
        wizard.product_id = product
        wizard.product_tmpl_id = product.product_tmpl_id
        wizard.new_quantity = qty
        wizard = wizard.save()
        wizard.change_product_qty()

    @classmethod
    def create_basic_so(cls, array_products):
        return cls.SaleOrder.create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": product["product"].id,
                            "name": "line 1",
                            "product_uom_qty": product["product_uom_qty"],
                            "qty_delivered": product["qty_delivered"],
                            "price_unit": 10,
                        },
                    )
                    for product in array_products
                ],
            }
        )
