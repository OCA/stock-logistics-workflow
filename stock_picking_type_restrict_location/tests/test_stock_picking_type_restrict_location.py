# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from contextlib import contextmanager

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import Form, tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestStockPickingTypeRestrictLocation(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Picking = cls.env["stock.picking"]
        cls.PickingType = cls.env["stock.picking.type"]
        cls.Location = cls.env["stock.location"]
        cls.Quant = cls.env["stock.quant"]
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.stock_location = cls.warehouse.lot_stock_id
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.zone_a = cls._create_location("Zone A", cls.stock_location)
        cls.bin_a = cls._create_location("Bin A1", cls.zone_a)
        cls.zone_b = cls._create_location("Zone B", cls.stock_location)
        cls.bin_b = cls._create_location("Bin B1", cls.zone_b)
        cls.zone_c = cls._create_location("Zone C", cls.stock_location)
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "is_storable": True}
        )
        cls.picking_type = cls.PickingType.create(
            {
                "name": "Zone A to Zone B",
                "code": "internal",
                "sequence_code": "A2B",
                "warehouse_id": cls.warehouse.id,
                "default_location_src_id": cls.zone_a.id,
                "default_location_dest_id": cls.zone_b.id,
                "restrict_location": True,
            }
        )

    @classmethod
    def _create_location(cls, name, parent, **kwargs):
        vals = {"name": name, "location_id": parent.id, "usage": "internal"}
        vals.update(kwargs)
        return cls.Location.create(vals)

    @classmethod
    def _create_picking(cls, **kwargs):
        vals = {
            "picking_type_id": cls.picking_type.id,
            "location_id": cls.bin_a.id,
            "location_dest_id": cls.bin_b.id,
        }
        vals.update(kwargs)
        vals["move_ids"] = [
            Command.create(
                {
                    "name": cls.product.name,
                    "product_id": cls.product.id,
                    "product_uom_qty": 5,
                    "product_uom": cls.product.uom_id.id,
                    "location_id": vals["location_id"],
                    "location_dest_id": vals["location_dest_id"],
                }
            )
        ]
        return cls.Picking.create(vals)

    @contextmanager
    def _assert_validation_error(self, message):
        with self.assertRaises(ValidationError) as error:
            yield
        self.assertIn(message, str(error.exception))

    def _process_picking(self, picking):
        picking.action_confirm()
        picking.action_assign()
        picking.button_validate()

    def test_transfer_between_sublocations(self):
        self.Quant._update_available_quantity(self.product, self.bin_a, 5)
        picking = self._create_picking()
        self._process_picking(picking)
        self.assertEqual(picking.state, "done")
        self.assertEqual(
            self.Quant._get_available_quantity(self.product, self.bin_b), 5
        )

    def test_transfer_outside_operation_type_locations(self):
        with self._assert_validation_error("cannot send stock to"):
            self._create_picking(location_dest_id=self.zone_c.id)
        with self._assert_validation_error("cannot take stock from"):
            self._create_picking(location_id=self.zone_c.id)
        picking = self._create_picking()
        with self._assert_validation_error("cannot send stock to"):
            picking.write({"location_dest_id": self.zone_c.id})
        with self._assert_validation_error("cannot take stock from"):
            picking.write({"location_id": self.stock_location.id})
        picking.write(
            {"location_id": self.zone_a.id, "location_dest_id": self.zone_b.id}
        )
        self.assertEqual(picking.location_id, self.zone_a)

    def test_automated_transfer_outside_operation_type_locations(self):
        move = self.env["stock.move"].create(
            {
                "name": self.product.name,
                "product_id": self.product.id,
                "product_uom_qty": 5,
                "product_uom": self.product.uom_id.id,
                "picking_type_id": self.picking_type.id,
                "location_id": self.zone_c.id,
                "location_dest_id": self.bin_b.id,
            }
        )
        with self._assert_validation_error("cannot take stock from"):
            move._action_confirm()

    def test_change_to_restricted_operation_type(self):
        self.picking_type.write({"restrict_location": False})
        free_type = self.picking_type.copy({"sequence_code": "FREE"})
        self.picking_type.write({"restrict_location": True})
        picking = self._create_picking(
            picking_type_id=free_type.id,
            location_id=self.zone_c.id,
            location_dest_id=self.stock_location.id,
        )
        picking.write({"picking_type_id": self.picking_type.id})
        self.assertEqual(picking.location_id, self.zone_a)
        self.assertEqual(picking.location_dest_id, self.zone_b)

    def test_free_operation_type(self):
        self.picking_type.write({"restrict_location": False})
        self.Quant._update_available_quantity(self.product, self.zone_c, 5)
        picking = self._create_picking(
            location_id=self.zone_c.id, location_dest_id=self.stock_location.id
        )
        self._process_picking(picking)
        self.assertEqual(picking.state, "done")

    def test_return_goes_back_and_cannot_be_diverted(self):
        self.Quant._update_available_quantity(self.product, self.bin_a, 5)
        picking = self._create_picking()
        self._process_picking(picking)
        wizard = Form(
            self.env["stock.return.picking"].with_context(
                active_id=picking.id,
                active_ids=picking.ids,
                active_model="stock.picking",
            )
        ).save()
        return_picking = self.Picking.browse(
            wizard.action_create_returns_all()["res_id"]
        )
        self.assertEqual(return_picking.picking_type_id, self.picking_type)
        self.assertEqual(return_picking.location_id, self.bin_b)
        self.assertEqual(return_picking.location_dest_id, self.bin_a)
        with self._assert_validation_error("cannot send stock to"):
            return_picking.write({"location_dest_id": self.zone_c.id})
        return_picking.button_validate()
        self.assertEqual(return_picking.state, "done")
        self.assertEqual(
            self.Quant._get_available_quantity(self.product, self.bin_a), 5
        )

    def test_receipt_restricts_only_the_destination(self):
        partner_location = self.Location.create(
            {"name": "Partner Vendors", "usage": "supplier"}
        )
        self.partner.write({"property_stock_supplier": partner_location.id})
        receipt_type = self.PickingType.create(
            {
                "name": "Receipts to Zone B",
                "code": "incoming",
                "sequence_code": "INB",
                "warehouse_id": self.warehouse.id,
                "default_location_src_id": self.supplier_location.id,
                "default_location_dest_id": self.zone_b.id,
                "restrict_location": True,
            }
        )
        picking = self.Picking.create(
            {"picking_type_id": receipt_type.id, "partner_id": self.partner.id}
        )
        self.assertEqual(picking.location_id, partner_location)
        self.assertEqual(picking.location_dest_id, self.zone_b)
        self.assertFalse(picking.allowed_location_ids)
        with self._assert_validation_error("cannot send stock to"):
            picking.write({"location_dest_id": self.zone_c.id})

    def test_delivery_restricts_only_the_source(self):
        partner_location = self.Location.create(
            {"name": "Partner Customers", "usage": "customer"}
        )
        self.partner.write({"property_stock_customer": partner_location.id})
        delivery_type = self.PickingType.create(
            {
                "name": "Deliveries from Zone A",
                "code": "outgoing",
                "sequence_code": "OUTA",
                "warehouse_id": self.warehouse.id,
                "default_location_src_id": self.zone_a.id,
                "default_location_dest_id": self.customer_location.id,
                "restrict_location": True,
            }
        )
        picking = self.Picking.create(
            {"picking_type_id": delivery_type.id, "partner_id": self.partner.id}
        )
        self.assertEqual(picking.location_id, self.zone_a)
        self.assertEqual(picking.location_dest_id, partner_location)
        self.assertFalse(picking.allowed_location_dest_ids)
        with self._assert_validation_error("cannot take stock from"):
            picking.write({"location_id": self.zone_c.id})

    def test_restrict_operation_type_with_transfers_in_progress(self):
        self.picking_type.write({"restrict_location": False})
        picking = self._create_picking(location_dest_id=self.zone_c.id)
        with self._assert_validation_error(picking.name):
            self.picking_type.write({"restrict_location": True})
        picking.write({"location_dest_id": self.bin_b.id})
        self.picking_type.write({"restrict_location": True})
        self.assertTrue(self.picking_type.restrict_location)
        with self._assert_validation_error(picking.name):
            self.picking_type.write({"default_location_dest_id": self.zone_c.id})

    def test_restrict_operation_type_with_rules(self):
        self.picking_type.write({"restrict_location": False})
        route = self.env["stock.route"].create({"name": "Zone C to Zone B"})
        rule = self.env["stock.rule"].create(
            {
                "name": "Zone C to Zone B",
                "route_id": route.id,
                "action": "pull",
                "picking_type_id": self.picking_type.id,
                "location_src_id": self.zone_c.id,
                "location_dest_id": self.zone_b.id,
            }
        )
        with self._assert_validation_error("takes stock from"):
            self.picking_type.write({"restrict_location": True})
        rule.write({"location_src_id": self.zone_a.id})
        self.picking_type.write({"restrict_location": True})
        self.assertTrue(self.picking_type.restrict_location)
        with self._assert_validation_error("takes stock from"):
            rule.write({"location_src_id": self.zone_c.id})
        with self._assert_validation_error("sends stock to"):
            rule.write({"action": "push", "location_dest_id": self.zone_c.id})
        rule.write({"active": False, "location_src_id": self.zone_c.id})
        with self._assert_validation_error("takes stock from"):
            rule.write({"active": True})
        production_location = self.Location.create(
            {"name": "Test Production", "usage": "production"}
        )
        rule.write({"active": True, "location_dest_id": production_location.id})
        self.assertEqual(rule.location_src_id, self.zone_c)

    def test_change_warehouse_delivery_steps(self):
        warehouse = self.env["stock.warehouse"].create(
            {"name": "Restricted Warehouse", "code": "RWH"}
        )
        delivery_type = warehouse.out_type_id
        delivery_type.write({"restrict_location": True})
        warehouse.write({"delivery_steps": "pick_ship"})
        self.assertEqual(
            delivery_type.default_location_src_id, warehouse.wh_output_stock_loc_id
        )
        warehouse.write({"delivery_steps": "ship_only"})
        self.assertEqual(delivery_type.default_location_src_id, warehouse.lot_stock_id)
        self.assertTrue(delivery_type.restrict_location)

    def test_change_warehouse_steps_with_transfer_in_progress(self):
        warehouse = self.env["stock.warehouse"].create(
            {
                "name": "Two Steps Warehouse",
                "code": "TSW",
                "delivery_steps": "pick_ship",
            }
        )
        pick_type = warehouse.pick_type_id
        pick_type.write({"restrict_location": True})
        picking = self.Picking.create({"picking_type_id": pick_type.id})
        self.assertEqual(picking.location_dest_id, warehouse.wh_output_stock_loc_id)
        with self._assert_validation_error(picking.name):
            warehouse.write({"delivery_steps": "ship_only"})
        picking.action_cancel()
        warehouse.write({"delivery_steps": "ship_only"})
        self.assertEqual(warehouse.delivery_steps, "ship_only")

    def test_restrict_operation_type_with_done_transfer_outside(self):
        self.picking_type.write({"restrict_location": False})
        self.Quant._update_available_quantity(self.product, self.zone_c, 5)
        picking = self._create_picking(
            location_id=self.zone_c.id, location_dest_id=self.stock_location.id
        )
        self._process_picking(picking)
        self.picking_type.write({"restrict_location": True})
        picking.write({"partner_id": self.partner.id})
        self.assertEqual(picking.location_id, self.zone_c)
        self.assertEqual(picking.partner_id, self.partner)

    def test_archived_operation_type_location(self):
        self.zone_b.write({"active": False})
        with self._assert_validation_error("cannot send stock to"):
            self._create_picking(location_dest_id=self.zone_c.id)
