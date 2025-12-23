# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


class TestStockPickingCarrier(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ResPartner = cls.env["res.partner"]
        Product = cls.env["product.product"]
        DeliveryCarrier = cls.env["delivery.carrier"]
        cls.product = Product.create(
            {
                "name": "Test Product",
            }
        )
        cls.delivery_carrier_id = DeliveryCarrier.create(
            {
                "name": "Test Carrier",
                "product_id": cls.product.id,
            }
        )
        cls.partner_id = ResPartner.create(
            {
                "name": "Test Carrier Partner",
                "property_delivery_carrier_id": cls.delivery_carrier_id.id,
            }
        )
        cls.location_src = cls.env["stock.location"].create(
            {
                "name": "Source Location",
                "usage": "internal",
            }
        )
        cls.location_dest = cls.env["stock.location"].create(
            {
                "name": "Destination Location",
                "usage": "internal",
            }
        )

    def enable_config_auto_assign(self):
        conf = self.env["res.config.settings"].create(
            {"carrier_auto_assign_picking": True}
        )
        conf.execute()

    def create_picking_type(self, assign_picking=True):
        picking_type_id = self.env["stock.picking.type"].create(
            {
                "name": "Test Picking Type",
                "code": "outgoing",
                "sequence_code": "OUT",
                "carrier_auto_assign_picking": assign_picking,
                "default_location_src_id": self.location_src.id,
                "default_location_dest_id": self.location_dest.id,
            }
        )
        return picking_type_id

    def _create_picking(self, assign_picking=True):
        return self.env["stock.picking"].create(
            {
                "picking_type_id": self.create_picking_type(assign_picking).id,
                "location_id": self.env.ref("stock.stock_location_customers").id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
            }
        )

    def test_onchange_partner_id_without_assign_auto(self):
        picking = self._create_picking(False)
        picking.partner_id = self.partner_id.id
        picking._onchange_partner_id()
        self.assertFalse(picking.carrier_id)

    def test_onchange_partner_id(self):
        self.enable_config_auto_assign()
        picking = self._create_picking()
        picking.partner_id = self.partner_id.id
        picking._onchange_partner_id()
        self.assertEqual(picking.carrier_id, self.delivery_carrier_id)

    def _create_sale_order(self):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner_id.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                        }
                    )
                ],
            }
        )

    def test_create_sale_order_without_assign_auto(self):
        self.env["stock.picking.type"].search([("sequence_code", "=", "OUT")]).write(
            {"carrier_auto_assign_picking": False}
        )
        sale_order = self._create_sale_order()
        sale_order.action_confirm()
        self.assertFalse(sale_order.picking_ids.carrier_id)

    def test_create_sale_order(self):
        self.enable_config_auto_assign()
        sale_order = self._create_sale_order()
        sale_order.action_confirm()
        self.assertEqual(sale_order.picking_ids.carrier_id, self.delivery_carrier_id)
