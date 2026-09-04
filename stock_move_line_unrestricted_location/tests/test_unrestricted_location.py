# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html)

from odoo.tests import Form
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestStockMoveWarehouseView(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env["stock.warehouse"].create(
            {
                "name": "Test Warehouse",
                "code": "TW",
            }
        )
        cls.view_location = cls.warehouse.view_location_id
        cls.src_location = cls.warehouse.lot_stock_id
        cls.dest_location = cls.env["stock.location"].create(
            {
                "name": "Test Destination Location",
                "usage": "internal",
                "location_id": cls.view_location.id,
            }
        )
        cls.extra_location = cls.env["stock.location"].create(
            {
                "name": "Test Extra Internal Location",
                "usage": "internal",
                "location_id": cls.view_location.id,
            }
        )

        cls.picking_type_in = cls.env["stock.picking.type"].create(
            {
                "name": "Test Incoming",
                "code": "incoming",
                "sequence_code": "TEST_IN",
                "warehouse_id": cls.warehouse.id,
                "default_location_src_id": cls.src_location.id,
                "default_location_dest_id": cls.dest_location.id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
            }
        )
        with Form(cls.env["stock.picking"]) as picking_form:
            picking_form.picking_type_id = cls.picking_type_in
            with picking_form.move_ids_without_package.new() as move:
                move.product_id = cls.product
                move.product_uom_qty = 10
            cls.picking = picking_form.save()

    def test_warehouse_unrestricted_domain(self):
        """Verify that moves can use any location within the same warehouse view"""
        # Force recomputation of stored related fields before assertions.
        self.env.flush_all()
        move = self.picking.move_ids_without_package[0]
        move.invalidate_recordset()

        self.assertEqual(move.warehouse_view_location_src_id.id, self.view_location.id)

        # Test form flexibility: change location
        # to a sibling (not a child of the current one).
        # This succeeds only if the domain uses the
        # warehouse view instead of the specific location.
        with Form(self.picking) as picking_form:
            with picking_form.move_ids_without_package.edit(0) as move_form:
                move_form.location_id = self.extra_location
                move_form.location_dest_id = self.dest_location

        self.assertEqual(move.location_id.id, self.extra_location.id)
