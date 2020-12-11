# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests import common


class CommonTest(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.product_model = cls.env["product.product"]
        cls.partner_model = cls.env["res.partner"]
        cls.product_tmpl_model = cls.env["product.template"]
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.env.ref("stock.picking_type_out").has_return_date = True

        cls.customer_a = cls.partner_model.create(
            {
                "name": "Customer Test",
                # "customer": True
            }
        )
        cls.template_a = cls.product_tmpl_model.create(
            {
                "name": "A",
                "type": "product",
                "list_price": 1,
                "tracking": "lot",
            }
        )
        cls.product_a = cls.template_a.product_variant_ids[0]
        cls.product_a_lot = cls.env["stock.production.lot"].create(
            {
                "name": "A-1",
                "product_id": cls.product_a.id,
                "company_id": cls.env.company.id,
            }
        )

    @classmethod
    def _update_quantity_onhand(cls, product, qty, location):

        cls.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": product.id,
                "location_id": location.id,
                "inventory_quantity": qty,
                "lot_id": cls.product_a_lot.id,
            }
        )

        # wizard_obj = cls.env["stock.change.product.qty"]
        # wizard = wizard_obj.create({
        #     "product_id": product.id,
        #     "new_quantity": qty,
        #     "location_id": location.id,
        # })
        # wizard.change_product_qty()

    @classmethod
    def get_product_qty(cls, product, location, lot_id=None):
        return cls.env["stock.quant"]._get_available_quantity(
            product, location, lot_id=lot_id
        )
