# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo.tests import Form

from odoo.addons.stock.tests.common import TestStockCommon


class TestBatchConfirm(TestStockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.location = cls.env["stock.location"].browse(cls.stock_location)
        vc_group = cls.env.ref(
            "stock_picking_batch_validate_confirm.stock_picking_batch_validate_confirm_group"
        )
        cls.env.ref("base.group_user").write({"implied_ids": [(4, vc_group.id)]})

    def create_pick_ship(self):
        picking_client = self.env["stock.picking"].create(
            {
                "location_id": self.pack_location,
                "location_dest_id": self.customer_location,
                "picking_type_id": self.picking_type_out,
            }
        )

        dest = self.MoveObj.create(
            {
                "name": self.productA.name,
                "product_id": self.productA.id,
                "product_uom_qty": 10,
                "product_uom": self.productA.uom_id.id,
                "picking_id": picking_client.id,
                "location_id": self.pack_location,
                "location_dest_id": self.customer_location,
                "state": "waiting",
                "procure_method": "make_to_order",
            }
        )

        picking_pick = self.env["stock.picking"].create(
            {
                "location_id": self.stock_location,
                "location_dest_id": self.pack_location,
                "picking_type_id": self.picking_type_out,
            }
        )

        self.MoveObj.create(
            {
                "name": self.productA.name,
                "product_id": self.productA.id,
                "product_uom_qty": 10,
                "product_uom": self.productA.uom_id.id,
                "picking_id": picking_pick.id,
                "location_id": self.stock_location,
                "location_dest_id": self.pack_location,
                "move_dest_ids": [(4, dest.id)],
                "state": "confirmed",
            }
        )
        return picking_pick, picking_client

    def test_batch_confirm(self):
        """Check batch confirm wizard when pending moves origin exist."""
        picking_pick_1, picking_client_1 = self.create_pick_ship()
        picking_pick_2, picking_client_2 = self.create_pick_ship()

        batch = self.env["stock.picking.batch"].create(
            {
                "name": "Batch 1",
                "company_id": self.env.company.id,
                "picking_ids": [
                    (4, picking_client_1.id),
                    (4, picking_client_2.id),
                ],
            }
        )
        self.env["stock.quant"]._update_available_quantity(
            self.productA, self.location, 10.0
        )
        (picking_pick_1 | picking_pick_2).action_assign()
        picking_pick_1.action_set_quantities_to_reservation()
        picking_pick_1._action_done()

        batch.action_set_quantities_to_reservation()
        res_dict = batch.action_done()
        self.assertEqual(res_dict.get("res_model"), "stock.picking.batch.confirm")
        wizard = Form(
            self.env[res_dict["res_model"]].with_context(**res_dict["context"])
        ).save()
        wizard.button_validate()
        self.assertEqual(batch.state, "done")
