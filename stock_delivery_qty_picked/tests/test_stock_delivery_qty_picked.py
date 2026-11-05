# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestStockDeliveryQtyPicked(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["res.config.settings"].create(
            {"group_stock_tracking_lot": True}
        ).execute()
        cls.wh = cls.env.ref("stock.warehouse0")
        cls.stock_location = cls.wh.out_type_id.default_location_src_id
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.wh.out_type_id.default_location_dest_id = cls.customer_location
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.uom_dozen = cls.env.ref("uom.product_uom_dozen")

        cls.prod_a = cls.env["product.product"].create(
            {
                "name": "Product A",
                "is_storable": True,
                "weight": 2.0,
                "uom_id": cls.uom_unit.id,
                "uom_po_id": cls.uom_unit.id,
            }
        )
        cls.prod_b = cls.env["product.product"].create(
            {
                "name": "Product B",
                "is_storable": True,
                "weight": 0.5,
                "uom_id": cls.uom_unit.id,
                "uom_po_id": cls.uom_unit.id,
            }
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.prod_a, cls.stock_location, 100.0
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.prod_b, cls.stock_location, 100.0
        )

        carrier_product = cls.env["product.product"].create(
            {"name": "Test carrier product", "type": "service"}
        )
        cls.carrier = cls.env["delivery.carrier"].create(
            {
                "name": "Test carrier",
                "delivery_type": "fixed",
                "product_id": carrier_product.id,
            }
        )
        cls.package_type = cls.env["stock.package.type"].create(
            {"name": "Test package type", "base_weight": 1.0}
        )

    @classmethod
    def _create_picking(cls, products_qties):
        """Create an outgoing picking with one move per product - qty tuple"""
        picking = cls.env["stock.picking"].create(
            {
                "partner_id": cls.partner.id,
                "picking_type_id": cls.wh.out_type_id.id,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.customer_location.id,
                "carrier_id": cls.carrier.id,
            }
        )
        for product, qty in products_qties:
            cls.env["stock.move"].create(
                {
                    "name": product.name,
                    "product_id": product.id,
                    "product_uom_qty": qty,
                    "product_uom": product.uom_id.id,
                    "picking_id": picking.id,
                    "location_id": cls.stock_location.id,
                    "location_dest_id": cls.customer_location.id,
                }
            )
        picking.action_confirm()
        picking.action_assign()
        return picking

    @classmethod
    def _open_pack_wizard(cls, picking, sml_ids=None):
        """Open the choose.delivery.package wizard as in the UI"""
        ctx = {}
        if sml_ids is not None:
            ctx["selected_smls_to_pack"] = sml_ids
        wiz_action = picking.with_context(**ctx).action_put_in_pack()
        wiz = Form.from_action(cls.env, wiz_action)
        wiz.delivery_package_type_id = cls.package_type
        return wiz.save()

    def test_wizard_weight_no_qty_picked(self):
        """Without touching qty_picked, weight is preserved"""
        picking = self._create_picking([(self.prod_a, 10.0)])
        picking.move_ids.picked = True
        # quantity == qty_picked == 10
        wiz = self._open_pack_wizard(picking)
        # base_weight(1) + 10 * weight(2)
        self.assertEqual(wiz.shipping_weight, 21.0)

    def test_wizard_weight_partial_pick(self):
        """qty_picked < quantity reduces shipping_weight"""
        picking = self._create_picking([(self.prod_a, 10.0)])
        move_line = picking.move_line_ids
        move_line.qty_picked = 6
        self.assertEqual(move_line.quantity, 10)
        self.assertEqual(move_line.qty_picked, 6)
        self.assertTrue(move_line.picked)
        wiz = self._open_pack_wizard(picking)
        # base_weight(1) + 6 * weight(2)
        self.assertEqual(wiz.shipping_weight, 13.0)

    def test_wizard_weight_picked_equal_quantity(self):
        """qty_picked == quantity, weight is correctly computed"""
        picking = self._create_picking([(self.prod_a, 4.0)])
        move_line = picking.move_line_ids
        move_line.qty_picked = 4
        wiz = self._open_pack_wizard(picking)
        # base_weight(1) + 4 * weight(2) = 9
        self.assertEqual(wiz.shipping_weight, 9.0)

    def test_wizard_weight_multi_line_mixed(self):
        """Mix of picked and partially picked move lines"""
        picking = self._create_picking([(self.prod_a, 10.0), (self.prod_b, 8.0)])
        mls = picking.move_line_ids
        ml_a = mls.filtered(lambda ml: ml.product_id == self.prod_a)
        ml_b = mls.filtered(lambda ml: ml.product_id == self.prod_b)
        # A: fully picked, B: partial pick.
        ml_a.qty_picked = 10
        ml_b.qty_picked = 5
        wiz = self._open_pack_wizard(picking)
        # base_weight(1) + 10 * weight(2) + 2 * weight(0.5)
        self.assertEqual(wiz.shipping_weight, 23.5)

    def test_wizard_weight_selected_smls_to_pack(self):
        """Only the selected move lines are taken into account"""
        picking = self._create_picking([(self.prod_a, 10.0), (self.prod_b, 8.0)])
        mls = picking.move_line_ids
        ml_a = mls.filtered(lambda ml: ml.product_id == self.prod_a)
        ml_b = mls.filtered(lambda ml: ml.product_id == self.prod_b)
        ml_a.qty_picked = 7
        ml_b.qty_picked = 4
        # Only pack line B
        wiz = self._open_pack_wizard(picking, sml_ids=ml_b.ids)
        # base_weight(1) + 4 * weight(0.5)
        self.assertEqual(wiz.shipping_weight, 3.0)

    def test_wizard_weight_uom_conversion(self):
        """qty_picked expressed in a non-product UoM is converted"""
        product = self.env["product.product"].create(
            {
                "name": "Product UoM",
                "is_storable": True,
                "weight": 1.0,
                "uom_id": self.uom_unit.id,
                "uom_po_id": self.uom_unit.id,
            }
        )
        self.env["stock.quant"]._update_available_quantity(
            product, self.stock_location, 100.0
        )
        picking = self.env["stock.picking"].create(
            {
                "partner_id": self.env["res.partner"]
                .create({"name": "Partner UoM"})
                .id,
                "picking_type_id": self.wh.out_type_id.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "carrier_id": self.carrier.id,
            }
        )
        self.env["stock.move"].create(
            {
                "name": product.name,
                "product_id": product.id,
                "product_uom_qty": 2.0,  # 2 dozen --> 24 units
                "product_uom": self.uom_dozen.id,
                "picking_id": picking.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
            }
        )
        picking.action_confirm()
        picking.action_assign()
        move_line = picking.move_line_ids
        # Move line UoM = dozen. Pick only 1 dozen = 12 units
        move_line.qty_picked = 1
        wiz = self._open_pack_wizard(picking)
        # base_weight(1) + 12 * weight(1)
        self.assertEqual(wiz.shipping_weight, 13.0)

    def test_package_weight_after_put_in_pack(self):
        """After put_in_pack, the package weight uses qty_picked"""
        picking = self._create_picking([(self.prod_a, 10.0)])
        move_line = picking.move_line_ids
        move_line.qty_picked = 4
        wiz = self._open_pack_wizard(picking)
        wiz.action_put_in_pack()
        package = picking.move_line_ids.result_package_id
        self.assertTrue(package)
        # Stored shipping_weight on the package matches wizard's computed value
        # base_weight(1) + 4 * weight(2)
        self.assertEqual(package.shipping_weight, 9.0)
        # And the computed package.weight (via _get_weight) for the picking
        # context reflects qty_picked too
        weight_for_picking = package.with_context(picking_id=picking.id).weight
        # base_weight(1) + 4 * weight(2)
        self.assertEqual(weight_for_picking, 9.0)

    def test_get_weight_no_picking_uses_super(self):
        """Without picking_id, _get_weight falls to super (quant-based)"""
        picking = self._create_picking([(self.prod_a, 6.0)])
        move_line = picking.move_line_ids
        move_line.qty_picked = 6
        wiz = self._open_pack_wizard(picking)
        wiz.action_put_in_pack()
        picking.with_context(skip_backorder=True).button_validate()
        package = picking.move_line_ids.result_package_id
        # Post-validation, _action_done has synced quantity = qty_picked,
        # so the no-picking branch (uses quants) is aligned
        weights = package._get_weight()
        # base_weight(1) + 4 * weight(2)
        self.assertEqual(weights[package], 13.0)

    def test_bulk_weight_no_qty_picked(self):
        """qty_picked == quantity: bulk weight equals super's value"""
        picking = self._create_picking([(self.prod_a, 10.0)])
        # picked=True with qty_picked auto-set to quantity through the inverse
        picking.move_ids.picked = True
        # 10 * 2 = 20
        self.assertEqual(picking.weight_bulk, 20.0)

    def test_bulk_weight_partial_pick(self):
        """qty_picked < quantity: bulk weight is reduced"""
        picking = self._create_picking([(self.prod_a, 10.0)])
        move_line = picking.move_line_ids
        move_line.qty_picked = 6
        # 6 * 2 = 12
        self.assertEqual(picking.weight_bulk, 12.0)

    def test_bulk_weight_excludes_packed_lines(self):
        """Lines that are in a result_package don't contribute to bulk weight"""
        picking = self._create_picking([(self.prod_a, 10.0)])
        move_line = picking.move_line_ids
        move_line.qty_picked = 8
        # Initially everything is bulk: 8 * 2 = 16
        self.assertEqual(picking.weight_bulk, 16.0)
        # Put it in a pack, bulk weight should drop to 0
        wiz = self._open_pack_wizard(picking)
        wiz.action_put_in_pack()
        self.assertEqual(picking.weight_bulk, 0.0)

    def test_bulk_weight_multi_line_mixed(self):
        """Bulk weight only reflects unpicked and unpacked lines"""
        picking = self._create_picking([(self.prod_a, 10.0), (self.prod_b, 8.0)])
        mls = picking.move_line_ids
        ml_a = mls.filtered(lambda ml: ml.product_id == self.prod_a)
        ml_b = mls.filtered(lambda ml: ml.product_id == self.prod_b)
        # A fully picked, B partially picked
        ml_a.qty_picked = 10
        ml_b.qty_picked = 5
        # 10 * 2 + 5 * 0.5 = 22.5
        self.assertEqual(picking.weight_bulk, 22.5)
        # Pack A, only B should remain in bulk
        wiz = self._open_pack_wizard(picking, sml_ids=ml_a.ids)
        wiz.with_context(default_move_line_ids=ml_a.ids).action_put_in_pack()
        # 5 * 0.5 = 2.5
        self.assertEqual(picking.weight_bulk, 2.5)

    def test_bulk_weight_recomputes_on_qty_picked_change(self):
        """Changing qty_picked re-triggers the bulk weight compute"""
        picking = self._create_picking([(self.prod_a, 10.0)])
        move_line = picking.move_line_ids
        move_line.qty_picked = 10
        self.assertEqual(picking.weight_bulk, 20.0)
        move_line.qty_picked = 7
        self.assertEqual(picking.weight_bulk, 14.0)

    def test_picking_shipping_weight_uses_qty_picked(self):
        """picking.shipping_weight (bulk + packed) reflects qty_picked"""
        picking = self._create_picking([(self.prod_a, 10.0), (self.prod_b, 8.0)])
        mls = picking.move_line_ids
        ml_a = mls.filtered(lambda ml: ml.product_id == self.prod_a)
        ml_b = mls.filtered(lambda ml: ml.product_id == self.prod_b)
        ml_a.qty_picked = 10
        ml_b.qty_picked = 5
        # Pack only A
        wiz = self._open_pack_wizard(picking, sml_ids=ml_a.ids)
        wiz.with_context(default_move_line_ids=ml_a.ids).action_put_in_pack()
        # bulk now only contains B: 5 * 0.5 = 2.5
        # packed A: base_weight(1) + 10 * 2 = 21
        # shipping_weight = 2.5 + 21 = 23.5
        self.assertEqual(picking.weight_bulk, 2.5)
        self.assertEqual(picking.shipping_weight, 23.5)
