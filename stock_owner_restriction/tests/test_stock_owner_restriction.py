# Copyright 2020 Carlos Dauden - Tecnativa
# Copyright 2020 Sergio Teruel - Tecnativa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.base.tests.common import BaseCommon


class TestStockOwnerRestriction(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # models
        cls.picking_model = cls.env["stock.picking"]
        cls.move_model = cls.env["stock.move"]
        cls.quant_model = cls.env["stock.quant"]
        cls.ResPartner = cls.env["res.partner"]

        # warehouse and picking types
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.source_location = cls.picking_type_out.default_location_src_id
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
            "location_id": cls.source_location.id,
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
                "location_id": cls.source_location.id,
                "location_dest_id": cls.customer_location.id,
            }
        )

    def _create_outgoing_picking(self, partner=None, owner=None, picking_type=None):
        picking_type = picking_type or self.picking_type_out
        vals = {
            "partner_id": partner.id if partner else False,
            "owner_id": owner.id if owner else False,
            "picking_type_id": picking_type.id,
            "location_id": self.source_location.id,
            "location_dest_id": self.customer_location.id,
        }
        return self.picking_model.with_context(
            default_picking_type_id=picking_type.id
        ).create(vals)

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
                picking_type_id=self.picking_type_out.id,
                product_uom_qty=1000.00,
                location_id=self.source_location.id,
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

    def test_search_qty(self):
        products = self.env["product.product"].search(
            [("id", "=", self.product.id), ("qty_available", ">", 500.00)]
        )
        self.assertFalse(products)
        products = self.env["product.product"].search(
            [("id", "=", self.product.id), ("qty_available", ">", 499.00)]
        )
        self.assertTrue(products)

    def test_search_qty_with_restricted_owner_context(self):
        products = (
            self.env["product.product"]
            .with_context(force_restricted_owner_id=self.owner.id)
            .search([("id", "=", self.product.id), ("qty_available", ">", 500.00)])
        )
        self.assertFalse(products)
        products = (
            self.env["product.product"]
            .with_context(force_restricted_owner_id=self.owner.id)
            .search([("id", "=", self.product.id), ("qty_available", ">", 499.00)])
        )
        self.assertTrue(products)

    def test_quant_restriction_owner_for_customer_location(self):
        owner = self.quant_model._get_restriction_owner_id(
            self.source_location, self.owner
        )
        self.assertEqual(owner, self.owner)
        owner = self.quant_model._get_restriction_owner_id(
            self.customer_location, self.owner
        )
        self.assertFalse(owner)

    def test_quant_available_quantity_with_forced_owner(self):
        qty_owner = self.quant_model.with_context(
            force_restricted_owner_id=self.owner
        )._get_available_quantity(self.product, self.source_location)
        self.assertEqual(qty_owner, 500.00)
        qty_unassigned = self.quant_model.with_context(
            force_restricted_owner_id=False
        )._get_available_quantity(self.product, self.source_location)
        self.assertEqual(qty_unassigned, 500.00)

    def test_quant_gather_with_forced_owner(self):
        owner_quants = self.quant_model.with_context(
            force_restricted_owner_id=self.owner
        )._gather(self.product, self.source_location, owner_id=self.owner)
        self.assertEqual(owner_quants.mapped("owner_id"), self.owner)
        unassigned_quants = self.quant_model.with_context(
            force_restricted_owner_id=False
        )._gather(self.product, self.source_location, owner_id=False)
        self.assertEqual(len(unassigned_quants), 1)
        self.assertFalse(unassigned_quants.owner_id)

    def test_get_owner_for_assign_priority(self):
        destination_picking = self._create_outgoing_picking(
            partner=self.customer, owner=self.owner
        )
        destination_move = self.move_model.create(
            {
                "product_id": self.product.id,
                "picking_id": destination_picking.id,
                "picking_type_id": self.picking_type_out.id,
                "product_uom_qty": 1.0,
                "location_id": self.source_location.id,
                "location_dest_id": self.customer_location.id,
                "product_uom": self.product.uom_id.id,
            }
        )
        source_picking = self._create_outgoing_picking(partner=self.customer)
        source_move = self.move_model.create(
            {
                "product_id": self.product.id,
                "picking_id": source_picking.id,
                "picking_type_id": self.picking_type_out.id,
                "product_uom_qty": 1.0,
                "location_id": self.source_location.id,
                "location_dest_id": self.customer_location.id,
                "product_uom": self.product.uom_id.id,
                "move_dest_ids": [(4, destination_move.id)],
            }
        )
        self.assertEqual(source_move._get_owner_for_assign(), self.owner)

        fallback_move = self.move_model.create(
            {
                "product_id": self.product.id,
                "picking_id": source_picking.id,
                "picking_type_id": self.picking_type_out.id,
                "product_uom_qty": 1.0,
                "location_id": self.source_location.id,
                "location_dest_id": self.customer_location.id,
                "product_uom": self.product.uom_id.id,
            }
        )
        self.assertEqual(fallback_move._get_owner_for_assign(), self.customer)

    def test_get_moves_to_assign_with_standard_behavior(self):
        standard_picking_type = self.picking_type_out.copy(
            {
                "name": "Test out standard",
                "sequence_code": "TSOS",
                "owner_restriction": "standard_behavior",
            }
        )
        self.picking_type_out.owner_restriction = "picking_partner"
        standard_picking = self._create_outgoing_picking(
            partner=self.customer, picking_type=standard_picking_type
        )
        restricted_picking = self._create_outgoing_picking(partner=self.customer)
        restricted_picking.picking_type_id.owner_restriction = "picking_partner"
        standard_move = self.move_model.create(
            {
                "product_id": self.product.id,
                "picking_id": standard_picking.id,
                "picking_type_id": standard_picking.picking_type_id.id,
                "product_uom_qty": 1.0,
                "location_id": self.source_location.id,
                "location_dest_id": self.customer_location.id,
                "product_uom": self.product.uom_id.id,
            }
        )
        restricted_move = self.move_model.create(
            {
                "product_id": self.product.id,
                "picking_id": restricted_picking.id,
                "picking_type_id": restricted_picking.picking_type_id.id,
                "product_uom_qty": 1.0,
                "location_id": self.source_location.id,
                "location_dest_id": self.customer_location.id,
                "product_uom": self.product.uom_id.id,
            }
        )
        moves = standard_move | restricted_move
        self.assertEqual(
            moves._get_moves_to_assign_with_standard_behavior(), standard_move
        )
