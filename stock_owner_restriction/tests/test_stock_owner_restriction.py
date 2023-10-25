# Copyright 2020 Carlos Dauden - Tecnativa
# Copyright 2020 Sergio Teruel - Tecnativa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestStockOwnerRestriction(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Remove this variable in v16 and put instead:
        # from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT
        DISABLED_MAIL_CONTEXT = {
            "tracking_disable": True,
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        # models
        cls.picking_model = cls.env["stock.picking"]
        cls.move_model = cls.env["stock.move"]
        cls.ResPartner = cls.env["res.partner"]

        # warehouse and picking types
        cls.warehouse = cls.env.ref("stock.stock_warehouse_shop0")
        cls.picking_type_out = cls.env.ref("stock.chi_picking_type_out")
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
            {"name": "Test restriction", "type": "product"}
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
        self.assertEqual(self.product.qty_available, 500.00)
        self.product.invalidate_model()
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
        self.assertEqual(self.picking_out.move_ids.reserved_availability, 1000.00)
        self.assertEqual(len(self.picking_out.move_line_ids), 2)
        self.assertEqual(self.picking_out.move_line_ids.mapped("owner_id"), self.owner)

        # Set restriction options on picking type to get only quants without
        # owner assigned
        self.picking_type_out.owner_restriction = "unassigned_owner"
        self.picking_out.do_unreserve()
        self.picking_out.action_assign()
        self.assertEqual(self.picking_out.move_ids.reserved_availability, 500.00)
        self.assertEqual(len(self.picking_out.move_line_ids), 1)
        self.assertFalse(self.picking_out.move_line_ids.mapped("owner_id"))

        # Set restriction options on picking type to get only quants with an
        # owner assigned.
        # The picking partner has not quants assigned so the picking is in
        # confirm state
        self.picking_type_out.owner_restriction = "picking_partner"
        self.picking_out.do_unreserve()
        self.picking_out.action_assign()
        self.assertEqual(self.picking_out.move_ids.reserved_availability, 0.0)
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
        self.assertEqual(self.picking_out.move_ids.reserved_availability, 500.00)
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
        self.assertEqual(self.picking_out.move_lines.reserved_availability, 1000.00)
        self.assertEqual(len(self.picking_out.move_line_ids), 2)
        self.assertEqual(self.picking_out.move_line_ids.mapped("owner_id"), self.owner)

        # Set restriction options on picking type to get only quants with an
        # owner assigned.
        # The picking partner has not quants assigned but there are unassigned quants
        # so the picking is in assigned state with 500 reserved units
        self.picking_out.partner_id = False
        self.picking_out.do_unreserve()
        self.picking_out.action_assign()
        self.assertEqual(self.picking_out.move_lines.reserved_availability, 500.00)
        self.assertEqual(len(self.picking_out.move_line_ids), 1)

    def test_search_qty(self):
        products = self.env["product.product"].search(
            [("id", "=", self.product.id), ("qty_available", ">", 500.00)]
        )
        self.assertFalse(products)
        products = self.env["product.product"].search(
            [("id", "=", self.product.id), ("qty_available", ">", 499.00)]
        )
        self.assertTrue(products)
