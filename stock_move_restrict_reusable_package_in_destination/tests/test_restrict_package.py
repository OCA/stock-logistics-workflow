# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from odoo.exceptions import ValidationError

from odoo.addons.base.tests.common import BaseCommon

_logger_name = (
    "odoo.addons.stock_move_restrict_reusable_package_in_destination."
    "models.stock_move_line"
)
_logger = logging.getLogger(_logger_name)


class TestPickingRestrict(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.delivery_steps = "pick_pack_ship"
        cls.customers = cls.env.ref("stock.stock_location_customers")

        cls.product = cls.env["product.product"].create(
            {
                "name": "Product",
                "is_storable": True,
            }
        )

        cls.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": cls.product.id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "inventory_quantity": 500.0,
            }
        )._apply_inventory()

        cls.package = cls.env["stock.quant.package"].create(
            {
                "name": "AA",
                "package_use": "reusable",
            }
        )
        cls.warehouse.pack_type_id.restrict_reusable_package_in_destination = True

    def _create_procurement(self):
        values = {"warehouse_id": self.warehouse}
        procurement = self.env["procurement.group"].Procurement(
            self.product,
            10,
            self.product.uom_id,
            self.customers,
            "Test",
            "Test",
            self.warehouse.company_id,
            values,
        )
        self.env["procurement.group"].run([procurement])

    def test_package_warning(self):
        self._create_procurement()
        move = self.env["stock.move"].search(
            [
                ("product_id", "=", self.product.id),
                ("location_id", "=", self.warehouse.lot_stock_id.id),
            ]
        )
        move.move_line_ids.picked = True
        move.move_line_ids.result_package_id = self.package
        move.picking_id._action_done()
        pack_move = move.move_dest_ids
        self.assertEqual(self.package, pack_move.move_line_ids.package_id)
        self.warehouse.pack_type_id.restrict_reusable_package_in_destination = False
        self.warehouse.pack_type_id.log_warning_reusable_package_in_destination = True
        message = (
            f"You cannot put the reusable package ({self.package.name}) "
            f"in picking ({pack_move.picking_id.name})! Check with your administrator."
        )

        with self.assertLogs(_logger, level="WARNING") as log_catcher:
            pack_move.move_line_ids.write({"result_package_id": self.package.id})
            pack_move.move_line_ids.invalidate_recordset()

        self.assertTrue(any(message in log.message for log in log_catcher.records))

    def test_package_exception(self):
        self._create_procurement()
        move = self.env["stock.move"].search(
            [
                ("product_id", "=", self.product.id),
                ("location_id", "=", self.warehouse.lot_stock_id.id),
            ]
        )
        move.move_line_ids.picked = True
        move.move_line_ids.result_package_id = self.package
        move.picking_id._action_done()
        pack_move = move.move_dest_ids
        self.assertEqual(self.package, pack_move.move_line_ids.package_id)
        message = (
            f"You cannot put the reusable package ({self.package.name}) "
            f"in picking ({pack_move.picking_id.name})! "
            "Check with your administrator."
        )
        with self.assertRaises(ValidationError) as exc_raises:
            pack_move.move_line_ids.result_package_id = self.package
        self.assertEqual(exc_raises.exception.args[0], message)

    def test_package_no_exception(self):
        self._create_procurement()
        move = self.env["stock.move"].search(
            [
                ("product_id", "=", self.product.id),
                ("location_id", "=", self.warehouse.lot_stock_id.id),
            ]
        )
        move.move_line_ids.picked = True
        move.move_line_ids.result_package_id = self.package
        move.picking_id._action_done()
        pack_move = move.move_dest_ids
        self.assertEqual(self.package, pack_move.move_line_ids.package_id)
        self.package.package_use = "disposable"
        pack_move.move_line_ids.result_package_id = self.package
