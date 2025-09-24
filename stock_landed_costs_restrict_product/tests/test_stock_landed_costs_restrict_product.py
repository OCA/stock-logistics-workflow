# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestStockLandedCost(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.StockPickingType = cls.env["stock.picking.type"]
        cls.StockLocation = cls.env["stock.location"]
        cls.StockPicking = cls.env["stock.picking"]
        cls.category_standard = cls.env["product.category"].create(
            {
                "name": "Landed Cost FIFO",
                "property_cost_method": "standard",
            }
        )
        cls.category_fifo = cls.env["product.category"].create(
            {
                "name": "Landed Cost FIFO",
                "property_cost_method": "fifo",
            }
        )
        cls.category_average = cls.env["product.category"].create(
            {
                "name": "Landed Cost Average",
                "property_cost_method": "average",
            }
        )
        cls.product_cost_equal = cls.env["product.template"].create(
            {
                "name": "Product Landed Cost Equal",
                "detailed_type": "service",
                "landed_cost_ok": True,
                "split_method_landed_cost": "equal",
            }
        )
        cls.product_cost_qty = cls.env["product.template"].create(
            {
                "name": "Product Landed Cost Quantity",
                "detailed_type": "service",
                "landed_cost_ok": True,
                "split_method_landed_cost": "by_quantity",
            }
        )
        cls.product_cost_price = cls.env["product.template"].create(
            {
                "name": "Product Landed Cost Price",
                "detailed_type": "service",
                "landed_cost_ok": True,
                "split_method_landed_cost": "by_current_cost_price",
            }
        )
        cls.product_cost_weight = cls.env["product.template"].create(
            {
                "name": "Product Landed Cost Weight",
                "detailed_type": "service",
                "landed_cost_ok": True,
                "split_method_landed_cost": "by_weight",
            }
        )
        cls.product_cost_volume = cls.env["product.template"].create(
            {
                "name": "Product Landed Cost Volume",
                "detailed_type": "service",
                "landed_cost_ok": True,
                "split_method_landed_cost": "by_volume",
            }
        )
        cls.product_category_fifo = cls.env["product.product"].create(
            {
                "name": "Product Landed Cost FIFO",
                "detailed_type": "product",
                "categ_id": cls.category_fifo.id,
                "standard_price": 50,
                "weight": 40,
                "volume": 45,
                "landed_cost_specific": True,
                "product_tmpl_landed_cost_ids": [
                    Command.set(
                        [
                            cls.product_cost_equal.id,
                            cls.product_cost_weight.id,
                            cls.product_cost_price.id,
                        ]
                    )
                ],
            }
        )
        cls.product_category_average = cls.env["product.product"].create(
            {
                "name": "Product Landed Cost average ",
                "detailed_type": "product",
                "categ_id": cls.category_average.id,
                "standard_price": 60,
                "weight": 50,
                "volume": 55,
                "landed_cost_specific": True,
                "product_tmpl_landed_cost_ids": [
                    Command.set(
                        [
                            cls.product_cost_qty.id,
                            cls.product_cost_price.id,
                            cls.product_cost_volume.id,
                        ]
                    )
                ],
            }
        )
        cls.stock_picking_type = cls.StockPickingType.create(
            {
                "name": "Test picking type",
                "sequence_code": "TEST",
            }
        )
        cls.stock_location_internal = cls.StockLocation.create(
            {
                "name": "Test location internal",
                "usage": "internal",
                "barcode": "8411322222111",
            }
        )

        cls.picking_id = cls.StockPicking.create(
            {
                "picking_type_id": cls.stock_picking_type.id,
                "move_ids_without_package": [
                    Command.create(
                        {
                            "name": cls.product_category_fifo.name,
                            "product_id": cls.product_category_fifo.id,
                            "product_uom_qty": 10,
                            "quantity": 10,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                            "location_id": cls.stock_location_internal.id,
                            "location_dest_id": cls.stock_location_internal.id,
                        }
                    ),
                    Command.create(
                        {
                            "name": cls.product_category_average.name,
                            "product_id": cls.product_category_average.id,
                            "product_uom_qty": 20,
                            "quantity": 20,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                            "location_id": cls.stock_location_internal.id,
                            "location_dest_id": cls.stock_location_internal.id,
                        }
                    ),
                ],
            }
        )

        cls.account_id = cls.env["account.account"].create(
            {
                "name": "Test asset current",
                "code": "TEST",
                "account_type": "asset_current",
            }
        )

    def create_landed_cost(self):
        landed_cost_id = self.env["stock.landed.cost"].create(
            {
                "company_id": self.env.company.id,
                "state": "draft",
                "picking_ids": [self.picking_id.id],
                "cost_lines": [
                    Command.create(
                        {
                            "product_id": self.product_cost_equal.product_variant_ids[
                                0
                            ].id,
                            "name": "Product Landed Cost",
                            "account_id": self.account_id.id,
                            "price_unit": 50,
                            "split_method": "equal",
                        }
                    ),
                    Command.create(
                        {
                            "product_id": self.product_cost_qty.product_variant_ids[
                                0
                            ].id,
                            "name": "Product Landed Cost 1",
                            "account_id": self.account_id.id,
                            "price_unit": 60,
                            "split_method": "by_quantity",
                        }
                    ),
                    Command.create(
                        {
                            "product_id": self.product_cost_volume.product_variant_ids[
                                0
                            ].id,
                            "name": "Product Landed Cost 1",
                            "account_id": self.account_id.id,
                            "price_unit": 70,
                            "split_method": "by_volume",
                        }
                    ),
                    Command.create(
                        {
                            "product_id": self.product_cost_weight.product_variant_ids[
                                0
                            ].id,
                            "name": "Product Landed Cost 1",
                            "account_id": self.account_id.id,
                            "price_unit": 70,
                            "split_method": "by_weight",
                        }
                    ),
                    Command.create(
                        {
                            "product_id": self.product_cost_price.product_variant_ids[
                                0
                            ].id,
                            "name": "Product Landed Cost 1",
                            "account_id": self.account_id.id,
                            "price_unit": 70,
                            "split_method": "by_current_cost_price",
                        }
                    ),
                ],
            }
        )
        return landed_cost_id

    def test_compute_landed_cost_apply_rule(self):
        self.env["ir.config_parameter"].set_param(
            "stock_landed_costs_product.landed_costs_apply_rule", True
        )
        landed_cost_id = self.create_landed_cost()
        self.picking_id.button_validate()
        landed_cost_id.compute_landed_cost()
        self.assertEqual(len(landed_cost_id.valuation_adjustment_lines), 6)
        landed_cost_id.button_validate()
        self.assertEqual(landed_cost_id.state, "done")

    def test_compute_landed_cost_not_apply_rule(self):
        self.env["ir.config_parameter"].set_param(
            "stock_landed_costs_product.landed_costs_apply_rule", False
        )
        self.picking_id.button_validate()
        landed_cost_id = self.create_landed_cost()
        landed_cost_id.compute_landed_cost()
        self.assertEqual(len(landed_cost_id.valuation_adjustment_lines), 10)
        landed_cost_id.button_validate()
        self.assertEqual(landed_cost_id.state, "done")

    def test_check_rule(self):
        self.env["ir.config_parameter"].set_param(
            "stock_landed_costs_product.landed_costs_apply_rule", True
        )
        landed_cost_id = self.create_landed_cost()
        landed_cost_id.compute_landed_cost()
        check_rule = landed_cost_id.valuation_adjustment_lines[0]._check_rule()
        self.assertTrue(check_rule)

        product_id = landed_cost_id.valuation_adjustment_lines[0].product_id
        product_id.product_tmpl_landed_cost_ids = [Command.clear()]
        check_rule = landed_cost_id.valuation_adjustment_lines[0]._check_rule()
        self.assertFalse(check_rule)

    def test_check_can_validate(self):
        self.product_cost_qty.categ_id = self.category_standard.id
        self.product_cost_volume.categ_id = self.category_standard.id
        self.product_cost_weight.categ_id = self.category_standard.id
        self.product_cost_price.categ_id = self.category_standard.id
        self.product_cost_equal.categ_id = self.category_standard.id
        self.env["ir.config_parameter"].set_param(
            "stock_landed_costs_product.landed_costs_apply_rule", True
        )
        landed_cost_id = self.create_landed_cost()
        with self.assertRaises(ValidationError):
            landed_cost_id._check_can_validate()
