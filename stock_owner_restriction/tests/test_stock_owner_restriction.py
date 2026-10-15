# Copyright 2020 Carlos Dauden - Tecnativa
# Copyright 2020 Sergio Teruel - Tecnativa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class TestStockOwnerRestriction(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        # models
        cls.picking_model = cls.env["stock.picking"]
        cls.move_model = cls.env["stock.move"]
        cls.ResPartner = cls.env["res.partner"]

        # warehouse and picking types
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")

        # Allow all companies for OdooBot user and set default user company
        # to warehouse company
        companies = cls.env["res.company"].search([])
        cls.env.user.company_ids = [(6, 0, companies.ids)]
        cls.env.user.company_id = cls.warehouse.company_id

        # customer
        cls.customer = cls.ResPartner.create({"name": "Customer test"})

        # Owner
        cls.owner = cls.ResPartner.create({"name": "Owner test"})

        # products
        cls.product = cls.env["product.product"].create(
            {"name": "Test restriction", "type": "consu", "is_storable": True}
        )
        quant_vals = {
            "product_id": cls.product.id,
            "location_id": cls.picking_type_out.default_location_src_id.id,
            "quantity": 500.00,
        }
        # Create quants without owner
        cls.env["stock.quant"].create(quant_vals)
        # Create quants with owner
        cls.env["stock.quant"].create(dict(quant_vals, owner_id=cls.owner.id))
        cls.picking_out = cls.picking_model.with_context(
            default_picking_type_id=cls.picking_type_out.id
        ).create(
            {
                "partner_id": cls.customer.id,
                "picking_type_id": cls.picking_type_out.id,
                "location_id": cls.picking_type_out.default_location_src_id.id,
                "location_dest_id": cls.customer_location.id,
            }
        )

    def test_product_qty_available(self):
        # Quants with owner assigned are not available
        # No need invalidate the cache, force_restricted_owner_id key is added to
        # context depends of product qty_available
        self.assertEqual(
            self.product.with_context(
                force_restricted_owner_id=self.owner.id
            ).qty_available,
            500.00,
        )
        self.assertEqual(
            self.product.with_context(skip_restricted_owner=True).qty_available, 1000.00
        )

    def test_restrict_reserve_qty(self):
        # Restrict quants from one owner to other customer
        self.move_model.create(
            dict(
                product_id=self.product.id,
                picking_id=self.picking_out.id,
                name=self.product.display_name,
                picking_type_id=self.picking_type_out.id,
                product_uom_qty=1000.00,
                location_id=self.picking_type_out.default_location_src_id.id,
                location_dest_id=self.customer_location.id,
                product_uom=self.product.uom_id.id,
            )
        )
        # Set restriction options on picking type
        self.picking_type_out.owner_restriction = "standard_behavior"
        self.picking_out.action_confirm()
        self.picking_out.action_assign()
        # For standard_behavior Odoo does not take into account the owner in
        # quants, so Odoo has been reserved 500 quantities without owner and
        # 500 quantities with owner
        self.assertEqual(self.picking_out.move_ids.quantity, 1000.00)
        self.assertEqual(len(self.picking_out.move_line_ids), 2)
        self.assertEqual(self.picking_out.move_line_ids.mapped("owner_id"), self.owner)

        # Set restriction options on picking type to get only quants without
        # owner assigned
        self.picking_type_out.owner_restriction = "unassigned_owner"
        self.picking_out.do_unreserve()
        self.picking_out.action_assign()
        self.assertEqual(self.picking_out.move_ids.quantity, 500.00)
        self.assertEqual(len(self.picking_out.move_line_ids), 1)
        self.assertFalse(self.picking_out.move_line_ids.mapped("owner_id"))

        # Set restriction options on picking type to get only quants with an
        # owner assigned.
        # The picking partner has not quants assigned so the picking is in
        # confirm state
        self.picking_type_out.owner_restriction = "picking_partner"
        self.picking_out.do_unreserve()
        self.picking_out.action_assign()
        self.assertEqual(self.picking_out.move_ids.quantity, 0.0)
        self.assertEqual(len(self.picking_out.move_line_ids), 0)
        self.assertEqual(self.picking_out.state, "confirmed")

        # Set restriction options on picking type to get only quants with an
        # owner assigned.
        # The picking partner has quants assigned so the picking is in
        # assigned state
        self.picking_type_out.owner_restriction = "picking_partner"
        self.picking_out.partner_id = self.owner
        self.picking_out.do_unreserve()
        self.picking_out.action_assign()
        self.assertEqual(self.picking_out.move_ids.quantity, 500.00)
        self.assertEqual(len(self.picking_out.move_line_ids), 1)
        self.assertTrue(self.picking_out.move_line_ids.mapped("owner_id"))
        self.assertEqual(self.picking_out.state, "assigned")

        # Set restriction options on picking type to get only quants with an
        # owner assigned.
        # The picking partner has quants assigned and there ara unassigned quants
        # so the picking is in assigned state and with 1000 reserved units
        self.picking_type_out.owner_restriction = "partner_or_unassigned"
        self.picking_out.do_unreserve()
        self.picking_out.action_assign()
        self.assertEqual(self.picking_out.move_ids.quantity, 1000.00)
        self.assertEqual(len(self.picking_out.move_line_ids), 2)
        self.assertEqual(self.picking_out.move_line_ids.mapped("owner_id"), self.owner)

        # Set restriction options on picking type to get only quants with an
        # owner assigned.
        # The picking partner has not quants assigned but there are unassigned quants
        # so the picking is in assigned state with 500 reserved units
        self.picking_out.partner_id = False
        self.picking_out.do_unreserve()
        self.picking_out.action_assign()
        self.assertEqual(self.picking_out.move_ids.quantity, 500.00)
        self.assertEqual(len(self.picking_out.move_line_ids), 1)

    def test_move_line_restricted_owner_fields(self):
        """The manual quant selector domain feeds on these helper fields."""
        self.picking_type_out.owner_restriction = "picking_partner"
        self.picking_out.partner_id = self.owner
        self.move_model.create(
            {
                "name": self.product.display_name,
                "product_id": self.product.id,
                "picking_id": self.picking_out.id,
                "product_uom_qty": 100.00,
                "product_uom": self.product.uom_id.id,
                "location_id": self.picking_type_out.default_location_src_id.id,
                "location_dest_id": self.customer_location.id,
            }
        )
        self.picking_out.action_confirm()
        self.picking_out.action_assign()
        move = self.picking_out.move_ids
        self.assertEqual(move.owner_restriction, "picking_partner")
        self.assertEqual(move.restricted_owner_id, self.owner)
        line = self.picking_out.move_line_ids
        self.assertEqual(line.owner_restriction, "picking_partner")
        self.assertEqual(line.restricted_owner_id, self.owner)

    def test_chained_moves_picking_partner(self):
        """Chained moves reserve under owner restriction without breaking.

        A pick brings owner stock to Output and the chained delivery must
        reserve it for the same partner. In 18.0 _action_assign prefetches a
        quants cache through stock.quant._read_group for chained moves, so
        this flow used to crash when the restriction context held a recordset.
        """
        picking_type_internal = self.env.ref("stock.picking_type_internal")
        output_location = self.env.ref("stock.stock_location_output")
        picking_type_internal.owner_restriction = "picking_partner"
        self.picking_type_out.owner_restriction = "picking_partner"
        pick = self.picking_model.create(
            {
                "partner_id": self.owner.id,
                "picking_type_id": picking_type_internal.id,
                "location_id": self.picking_type_out.default_location_src_id.id,
                "location_dest_id": output_location.id,
            }
        )
        pick_move = self.move_model.create(
            {
                "name": self.product.display_name,
                "product_id": self.product.id,
                "picking_id": pick.id,
                "product_uom_qty": 100.00,
                "product_uom": self.product.uom_id.id,
                "location_id": self.picking_type_out.default_location_src_id.id,
                "location_dest_id": output_location.id,
            }
        )
        ship = self.picking_model.create(
            {
                "partner_id": self.owner.id,
                "picking_type_id": self.picking_type_out.id,
                "location_id": output_location.id,
                "location_dest_id": self.customer_location.id,
            }
        )
        ship_move = self.move_model.create(
            {
                "name": self.product.display_name,
                "product_id": self.product.id,
                "picking_id": ship.id,
                "product_uom_qty": 100.00,
                "product_uom": self.product.uom_id.id,
                "location_id": output_location.id,
                "location_dest_id": self.customer_location.id,
                "move_orig_ids": [(4, pick_move.id)],
                "procure_method": "make_to_order",
            }
        )
        (pick | ship).action_confirm()
        pick.action_assign()
        self.assertEqual(pick_move.quantity, 100.00)
        self.assertEqual(pick.move_line_ids.owner_id, self.owner)
        pick.move_line_ids.picked = True
        pick.button_validate()
        ship.action_assign()
        self.assertEqual(ship_move.quantity, 100.00)
        self.assertEqual(ship.move_line_ids.owner_id, self.owner)

    def test_set_quantity_done_import_unassigned_owner(self):
        """Writing move.quantity directly must still respect the restriction.

        This is what a stock.picking import does via
        move_ids_without_package/quantity (as opposed to product_uom_qty
        alone): it reserves through stock.move._set_quantity's inverse,
        entirely bypassing _action_assign. Reproduces the WH/OUT/723826
        incident, where that path grabbed a quant owned by a different
        partner because it was older (lower in_date) than the free stock.
        """
        self.picking_type_out.owner_restriction = "unassigned_owner"
        owned_quant = self.env["stock.quant"].search(
            [("product_id", "=", self.product.id), ("owner_id", "=", self.owner.id)]
        )
        owned_quant.in_date = "2000-01-01 00:00:00"

        fields_list = [
            "partner_id/.id",
            "picking_type_id/.id",
            "location_id/.id",
            "location_dest_id/.id",
            "move_ids_without_package/product_id/.id",
            "move_ids_without_package/name",
            "move_ids_without_package/product_uom_qty",
            "move_ids_without_package/quantity",
        ]
        row = [
            str(self.customer.id),
            str(self.picking_type_out.id),
            str(self.picking_type_out.default_location_src_id.id),
            str(self.customer_location.id),
            str(self.product.id),
            self.product.display_name,
            "500",
            "500",
        ]
        result = self.picking_model.load(fields_list, [row])
        self.assertFalse(result["messages"], result["messages"])
        picking = self.picking_model.browse(result["ids"][0])
        self.assertEqual(sum(picking.move_line_ids.mapped("quantity")), 500.00)
        self.assertFalse(picking.move_line_ids.mapped("owner_id"))

    def test_search_qty(self):
        products = self.env["product.product"].search(
            [("id", "=", self.product.id), ("qty_available", ">", 500.00)]
        )
        self.assertFalse(products)
        products = self.env["product.product"].search(
            [("id", "=", self.product.id), ("qty_available", ">", 499.00)]
        )
        self.assertTrue(products)
