from odoo.addons.stock_landed_costs_purchase_auto.tests.common import (
    TestPurchaseOrderBase,
)


class TestPurchaseStockLandedCostEstimateBase(TestPurchaseOrderBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.supplierinfo = cls.env["product.supplierinfo"].create(
            {
                "partner_id": cls.partner.id,
                "product_id": cls.product_storable.id,
                "product_code": "test",
                "price": 10,
                "indirect_cost_percent": 10,
            }
        )
        cls.order.order_line.price_unit = 10
