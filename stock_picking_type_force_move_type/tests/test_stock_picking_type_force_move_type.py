# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields

from odoo.addons.base.tests.common import BaseCommon


class TestPickingTypeForceMoveType(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        # set pick-pack-ship on warehouse
        cls.warehouse.delivery_steps = "pick_pack_ship"
        cls.pick_type = cls.warehouse.pick_type_id
        cls.pack_type = cls.warehouse.pack_type_id
        cls.ship_type = cls.warehouse.out_type_id

        cls.customers_location = cls.env.ref("stock.stock_location_customers")
        cls.output_location = cls.warehouse.wh_output_stock_loc_id

        cls.product = cls.env.ref("product.product_product_9")
        # Create ir.default for procure_method as make_to_order in order to
        #  generate chained moves
        cls.env["ir.default"].create(
            {
                "field_id": cls.env.ref("stock.field_stock_move__procure_method").id,
                "json_value": '"make_to_order"',
            }
        )

    def _run_procurement(self, product, qty):
        moves_before = self.env["stock.move"].search([])
        proc_group = self.env["procurement.group"]
        uom = product.uom_id
        proc_qty, proc_uom = uom._adjust_uom_quantities(qty, uom)
        today = fields.Date.today()
        proc_group = self.env["procurement.group"].create({})
        values = {
            "group_id": proc_group,
            "date_planned": today,
            "date_deadline": today,
            "warehouse_id": self.warehouse or False,
            "company_id": self.company,
        }
        procurement = proc_group.Procurement(
            product,
            proc_qty,
            proc_uom,
            self.customers_location,
            product.name,
            "PROC TEST",
            self.company,
            values,
        )
        proc_group.run([procurement])
        moves_after = self.env["stock.move"].search([])
        return moves_after - moves_before

    def _validate_picking(self, picking):
        picking.move_line_ids.write({"picked": True})
        picking._action_done()

    def test_force_move_type(self):
        self.pack_type.write({"move_type": "one", "force_move_type": True})
        self.pick_type.write({"move_type": "direct", "force_move_type": True})
        move = self._run_procurement(self.product, 10)
        pick_picking = move.picking_id
        self._validate_picking(pick_picking)
        self.assertEqual(pick_picking.state, "done")
        pack_picking = pick_picking.move_ids.move_dest_ids.picking_id
        self.assertEqual(pack_picking.picking_type_id, self.pack_type)
        self.assertEqual(pack_picking.move_type, "one")
        self.assertEqual(pick_picking.picking_type_id, self.pick_type)
        self.assertEqual(pick_picking.move_type, "direct")
