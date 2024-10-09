# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestStockMovePickingTypeOrigin(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.groups_id += cls.env.ref(
            "stock.group_stock_multi_locations"
        ) | cls.env.ref("stock.group_adv_location")
        cls.product_model = cls.env["product.product"]
        cls.stock_model = cls.env["stock.move"]
        cls.product = cls.product_model.create({"name": "product", "type": "product"})
        cls.warehouse = cls.env["stock.warehouse"].search([], limit=1)
        cls.loc_stock = cls.warehouse.lot_stock_id
        cls.loc_out = cls.env.ref("stock.stock_location_output")
        cls.loc_in_1 = cls.warehouse.wh_input_stock_loc_id
        cls.loc_in_2 = cls.loc_out.copy({"name": "Input 2"})
        cls.loc_customer = cls.env.ref("stock.stock_location_customers")
        cls.loc_supplier = cls.env.ref("stock.stock_location_suppliers")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.picking_type_inter = cls.env.ref("stock.picking_type_internal")
