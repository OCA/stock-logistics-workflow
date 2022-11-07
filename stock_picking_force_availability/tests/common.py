# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests.common import Form, SavepointCase


class Common(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.product = cls.env["product.product"].create(
            {
                "name": "TEST PRODUCT",
                "type": "product",
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "TEST PRODUCT2",
                "type": "product",
            }
        )
        cls.picking_assigned = cls._create_picking(
            cls.picking_type_out,
            lines=[
                (cls.product, cls.picking_type_out.default_location_src_id, 10),
            ],
        )
        cls.picking_confirmed = cls._create_picking(
            cls.picking_type_out,
            lines=[
                (cls.product, cls.picking_type_out.default_location_src_id, 10),
            ],
            put_stock=False,
        )

    @classmethod
    def _create_picking(cls, picking_type, lines, put_stock=True):
        picking_form = Form(cls.env["stock.picking"])
        picking_form.picking_type_id = picking_type
        for product, location, qty in lines:
            if put_stock:
                cls.env["stock.quant"]._update_available_quantity(
                    product, location, qty
                )
            with picking_form.move_ids_without_package.new() as move:
                move.product_id = product
                move.product_uom_qty = qty
        picking = picking_form.save()
        picking.action_confirm()
        picking.action_assign()
        return picking

    @classmethod
    def get_force_availability_wizard(cls, picking):
        wiz_model = cls.env["stock.picking.force_availability"].with_context(
            active_model=picking._name,
            active_id=picking.id,
        )
        with Form(wiz_model) as form:
            return form.save()
