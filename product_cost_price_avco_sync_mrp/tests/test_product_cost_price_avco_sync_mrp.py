# Copyright 2019 Tecnativa - Carlos Dauden
# Copyright 2019 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo.tests.common import Form, SavepointCase, tagged

_logger = logging.getLogger(__name__)


@tagged("-at_install", "post_install")
class TestProductCostPriceAvcoSync(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.StockPicking = cls.env["stock.picking"]
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.categ_all = cls.env.ref("product.product_category_all")
        cls.categ_all.property_cost_method = "average"
        cls.prod_material_1 = cls.env["product.product"].create(
            {
                "name": "Material 1",
                "type": "product",
                "tracking": "none",
                "standard_price": 0.5,
                "categ_id": cls.categ_all.id,
            }
        )
        cls.prod_material_2 = cls.env["product.product"].create(
            {
                "name": "Material 2",
                "type": "product",
                "tracking": "none",
                "standard_price": 0.6,
                "categ_id": cls.categ_all.id,
            }
        )
        cls.prod_produced = cls.env["product.product"].create(
            {
                "name": "Product Produced",
                "type": "product",
                "tracking": "none",
                "categ_id": cls.categ_all.id,
            }
        )
        cls.picking_in = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.picking_type_in.id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.stock_location.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "a move",
                            "product_id": cls.prod_material_1.id,
                            "product_uom_qty": 10.0,
                            "product_uom": cls.prod_material_1.uom_id.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "b move",
                            "product_id": cls.prod_material_2.id,
                            "product_uom_qty": 10.0,
                            "product_uom": cls.prod_material_2.uom_id.id,
                        },
                    ),
                ],
            }
        )
        cls.env["stock.immediate.transfer"].create(
            {"pick_ids": [(4, cls.picking_in.id)]}
        ).process()
        cls.picking_in.action_done()
        materials_list = [(cls.prod_material_1, 10), (cls.prod_material_2, 10)]
        cls.production = cls._do_production_process(
            cls, materials_list, cls.prod_produced, 1
        )

    def _do_production_process(
        self, materials, produced_id, qty_produced, extra_cost=0
    ):
        mrp_bom_form = Form(self.env["mrp.bom"])
        mrp_bom_form.product_id = produced_id
        mrp_bom_form.product_tmpl_id = produced_id.product_tmpl_id
        mrp_bom_form.product_qty = qty_produced
        for material, qty in materials:
            with mrp_bom_form.bom_line_ids.new() as consumed_line:
                consumed_line.product_id = material
                consumed_line.product_qty = qty
        mrp_bom_form.save()
        mrp_production_form = Form(self.env["mrp.production"])
        mrp_production_form.product_id = produced_id
        production = mrp_production_form.save()
        production.extra_cost = extra_cost
        production.action_confirm()
        production.action_assign()
        wiz_form = Form(
            self.env["mrp.product.produce"].with_context(
                {
                    "active_model": "mrp.production",
                    "active_id": production.id,
                    "active_ids": [production.id],
                }
            )
        )
        wiz = wiz_form.save()
        wiz.do_produce()
        production.button_mark_done()
        return production

    def test_sync_cost_price_1_prod(self):
        self.assertEqual(self.prod_produced.standard_price, 11.0)
        # Change value of prod_material_1
        self.picking_in.move_lines.filtered(
            lambda ml: ml.product_id == self.prod_material_1
        ).stock_valuation_layer_ids.write({"unit_cost": 1})
        self.assertEqual(self.prod_produced.standard_price, 16.0)
        # Change value of prod_material_2
        self.picking_in.move_lines.filtered(
            lambda ml: ml.product_id == self.prod_material_2
        ).stock_valuation_layer_ids.write({"unit_cost": 0.2})
        self.assertEqual(self.prod_produced.standard_price, 12.0)
        # Change value of both materials
        self.picking_in.move_lines.stock_valuation_layer_ids.write({"unit_cost": 0.3})
        self.assertEqual(self.prod_produced.standard_price, 6)
        # Change qty of first material
        self.production.move_raw_ids.filtered(
            lambda mr: mr.product_id == self.prod_material_1
        ).move_line_ids.write({"qty_done": 5})
        self.assertEqual(self.prod_produced.standard_price, 4.5)
        # Change qty of second material
        self.production.move_raw_ids.filtered(
            lambda mr: mr.product_id == self.prod_material_2
        ).move_line_ids.write({"qty_done": 5})
        self.assertEqual(self.prod_produced.standard_price, 3)
        # Change qty of product
        self.production.finished_move_line_ids.filtered(
            lambda ml: ml.product_id == self.prod_produced
        ).write({"qty_done": 2})
        self.assertEqual(self.prod_produced.standard_price, 1.5)

    def test_sync_cost_price_chained_prod(self):
        prod_chain_produced = self.env["product.product"].create(
            {
                "name": "Product Chain Produced",
                "type": "product",
                "tracking": "none",
                "categ_id": self.categ_all.id,
            }
        )
        final_production = self._do_production_process(
            [(self.prod_produced, 1)], prod_chain_produced, 5
        )
        self.assertAlmostEqual(prod_chain_produced.standard_price, 2.2)
        # Change value of prod_material_1
        self.picking_in.move_lines.filtered(
            lambda ml: ml.product_id == self.prod_material_1
        ).stock_valuation_layer_ids.write({"unit_cost": 1})
        self.assertAlmostEqual(prod_chain_produced.standard_price, 3.2)
        # Change value of prod_material_2
        self.picking_in.move_lines.filtered(
            lambda ml: ml.product_id == self.prod_material_2
        ).stock_valuation_layer_ids.write({"unit_cost": 0.2})
        self.assertAlmostEqual(prod_chain_produced.standard_price, 2.4)
        # Change value of both materials
        self.picking_in.move_lines.stock_valuation_layer_ids.write({"unit_cost": 0.3})
        self.assertAlmostEqual(prod_chain_produced.standard_price, 1.2)
        # Change qty of first material
        self.production.move_raw_ids.filtered(
            lambda mr: mr.product_id == self.prod_material_1
        ).move_line_ids.write({"qty_done": 5})
        self.assertEqual(prod_chain_produced.standard_price, 0.9)
        # Change qty of second material
        self.production.move_raw_ids.filtered(
            lambda mr: mr.product_id == self.prod_material_2
        ).move_line_ids.write({"qty_done": 5})
        self.assertEqual(prod_chain_produced.standard_price, 0.6)
        # Change qty of product
        self.production.finished_move_line_ids.filtered(
            lambda ml: ml.product_id == self.prod_produced
        ).write({"qty_done": 2})
        self.assertEqual(prod_chain_produced.standard_price, 0.3)
        # Change qty of final product
        final_production.finished_move_line_ids.filtered(
            lambda ml: ml.product_id == prod_chain_produced
        ).write({"qty_done": 2})
        self.assertEqual(prod_chain_produced.standard_price, 0.75)

    def test_multiple_moves_1_product_material(self):
        prod_material_multiple = self.env["product.product"].create(
            {
                "name": "Material Multiple Price",
                "type": "product",
                "tracking": "none",
                "categ_id": self.categ_all.id,
            }
        )
        picking_in_1 = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type_in.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "move",
                            "product_id": prod_material_multiple.id,
                            "product_uom_qty": 10.0,
                            "product_uom": prod_material_multiple.uom_id.id,
                            "price_unit": 1,
                        },
                    ),
                ],
            }
        )
        self.env["stock.immediate.transfer"].create(
            {"pick_ids": [(4, picking_in_1.id)]}
        ).process()
        picking_in_1.action_done()
        picking_in_2 = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type_in.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "move",
                            "product_id": prod_material_multiple.id,
                            "product_uom_qty": 5.0,
                            "product_uom": prod_material_multiple.uom_id.id,
                            "price_unit": 2,
                        },
                    ),
                ],
            }
        )
        self.env["stock.immediate.transfer"].create(
            {"pick_ids": [(4, picking_in_2.id)]}
        ).process()
        picking_in_2.action_done()
        self.assertAlmostEqual(prod_material_multiple.standard_price, 1.33)
        prod_produced_multiple = self.env["product.product"].create(
            {
                "name": "Product Produced Multi",
                "type": "product",
                "tracking": "none",
                "categ_id": self.categ_all.id,
            }
        )
        self._do_production_process(
            [(prod_material_multiple, 5)], prod_produced_multiple, 1
        )
        self.assertAlmostEqual(prod_produced_multiple.standard_price, 6.65)
        # Change price of 2nd move from 2 to 1
        picking_in_2.move_lines.stock_valuation_layer_ids.write({"unit_cost": 1})
        self.assertAlmostEqual(prod_material_multiple.standard_price, 1)
        self.assertAlmostEqual(prod_produced_multiple.standard_price, 5)

    def test_production_with_extra_cost(self):
        prod_material_multiple = self.env["product.product"].create(
            {
                "name": "Material Multiple Price",
                "type": "product",
                "tracking": "none",
                "categ_id": self.categ_all.id,
            }
        )
        picking_in_1 = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type_in.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "move",
                            "product_id": prod_material_multiple.id,
                            "product_uom_qty": 10.0,
                            "product_uom": prod_material_multiple.uom_id.id,
                            "price_unit": 1,
                        },
                    ),
                ],
            }
        )
        self.env["stock.immediate.transfer"].create(
            {"pick_ids": [(4, picking_in_1.id)]}
        ).process()
        picking_in_1.action_done()
        picking_in_2 = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type_in.id,
                "location_id": self.supplier_location.id,
                "location_dest_id": self.stock_location.id,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "move",
                            "product_id": prod_material_multiple.id,
                            "product_uom_qty": 5.0,
                            "product_uom": prod_material_multiple.uom_id.id,
                            "price_unit": 2,
                        },
                    ),
                ],
            }
        )
        self.env["stock.immediate.transfer"].create(
            {"pick_ids": [(4, picking_in_2.id)]}
        ).process()
        picking_in_2.action_done()
        self.assertAlmostEqual(prod_material_multiple.standard_price, 1.33)
        prod_produced_multiple = self.env["product.product"].create(
            {
                "name": "Product Produced Multi",
                "type": "product",
                "tracking": "none",
                "categ_id": self.categ_all.id,
            }
        )
        self._do_production_process(
            [(prod_material_multiple, 5)], prod_produced_multiple, 1, extra_cost=5
        )
        self.assertAlmostEqual(prod_produced_multiple.standard_price, 11.65)
        # Change price of 2nd move from 2 to 1
        picking_in_2.move_lines.stock_valuation_layer_ids.write({"unit_cost": 1})
        self.assertAlmostEqual(prod_material_multiple.standard_price, 1)
        self.assertAlmostEqual(prod_produced_multiple.standard_price, 10)
