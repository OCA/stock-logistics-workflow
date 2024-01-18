# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests.common import Form, SavepointCase


class TestMTOVariantCommon(SavepointCase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.setUpClassProduct()


    @classmethod
    def setUpClassProduct(cls):
        cls.color = cls.env['product.attribute'].create({'name': 'Color'})
        value_model = cls.env['product.attribute.value']
        cls.values = value_model.create(
            [
                {'name': 'red', 'attribute_id': cls.color.id},
                {'name': 'blue', 'attribute_id': cls.color.id},
                {'name': 'black', 'attribute_id': cls.color.id},
                {'name': 'green', 'attribute_id': cls.color.id},
            ]
        )
        cls.value_red = cls.values.filtered(lambda v: v.name == "red")
        cls.value_blue = cls.values.filtered(lambda v: v.name == "blue")
        cls.value_black = cls.values.filtered(lambda v: v.name == "black")
        cls.value_green = cls.values.filtered(lambda v: v.name == "green")
        cls.template_pen = cls.env["product.template"].create(
            {
                "name": "pen",
                'attribute_line_ids': [
                    (0, 0, {
                        'attribute_id': cls.color.id,
                        'value_ids': [(6, 0, cls.values.ids)],
                    })
                ]
            }
        )
        cls.variants_pen = cls.template_pen.product_variant_ids
        cls.black_pen = cls.variants_pen.filtered(lambda v: v.product_template_attribute_value_ids.name == "black")
        cls.green_pen = cls.variants_pen.filtered(lambda v: v.product_template_attribute_value_ids.name == "green")
        cls.red_pen = cls.variants_pen.filtered(lambda v: v.product_template_attribute_value_ids.name == "red")
        cls.blue_pen = cls.variants_pen.filtered(lambda v: v.product_template_attribute_value_ids.name == "blue")
        cls.mto_route = cls.env.ref("stock.route_warehouse0_mto")
        cls.mto_route.active = True

    def add_route(self, template, route):
        if not route:
            route = self.mto_route
        with Form(template) as record:
            record.route_ids.add(route)

    def remove_route(self, template, route):
        if not route:
            route = self.mto_route
        with Form(template) as record:
            record.route_ids.remove(id=route.id)

    @classmethod
    def toggle_is_mto(self, records):
        for record in records:
            record.is_mto = not record.is_mto

    def assertVariantsMTO(self, records):
        records.invalidate_cache(["is_mto"])
        self.assertTrue(all([record.is_mto for record in records]))
        for rec in records:
            self.assertIn(self.mto_route, rec.route_ids)

    def assertVariantsNotMTO(self, records):
        records.invalidate_cache(["is_mto"])
        self.assertFalse(any([record.is_mto for record in records]))
        for rec in records:
            self.assertNotIn(self.mto_route, rec.route_ids)
