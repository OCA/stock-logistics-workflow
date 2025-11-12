# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo.exceptions import UserError

from odoo.addons.stock.tests.common import TestStockCommon


class StockPickingToBatchGroupField(TestStockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.BatchObject = cls.env["stock.picking.batch"]
        cls.pickingA = cls.PickingObj.with_context(planned=True).create(
            {
                "picking_type_id": cls.picking_type_out,
                "location_id": cls.stock_location,
                "location_dest_id": cls.customer_location,
                "origin": "A",
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test move",
                            "product_id": cls.productA.id,
                            "product_uom_qty": 1,
                            "location_id": cls.stock_location,
                            "location_dest_id": cls.customer_location,
                        },
                    )
                ],
            }
        )
        cls.pickingB = cls.PickingObj.with_context(planned=True).create(
            {
                "picking_type_id": cls.picking_type_out,
                "location_id": cls.stock_location,
                "location_dest_id": cls.customer_location,
                "origin": "B",
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test move",
                            "product_id": cls.productB.id,
                            "product_uom_qty": 1,
                            "location_id": cls.stock_location,
                            "location_dest_id": cls.customer_location,
                        },
                    )
                ],
            }
        )
        cls.pickings = cls.pickingA + cls.pickingB
        cls.batch = cls.BatchObject.create({})

    def test_sptb_existing_batch(self):
        """Add pickings to existing batch"""
        self.env["stock.picking.to.batch"].with_context(
            active_ids=self.pickings.ids
        ).create(
            {
                "batch_id": self.batch.id,
                "mode": "existing",
            }
        ).attach_pickings()
        self.assertEqual(len(self.pickings.mapped("batch_id")), 1)
        self.assertEqual(self.pickingA.batch_id, self.batch)
        self.assertEqual(self.pickingB.batch_id, self.batch)

    def test_sptb_new_batch_no_groupby(self):
        """Add pickings to new batch and not groupby"""
        self.env["stock.picking.to.batch"].with_context(
            active_ids=self.pickings.ids
        ).create(
            {
                "mode": "new",
                "batch_by_group": False,
                "group_field_ids": False,
            }
        ).attach_pickings()
        self.assertEqual(len(self.pickings.mapped("batch_id")), 1)

    def test_sptb_new_batch_groupby_no_fields(self):
        """Add picking to new batch and groupby checked but no fields"""
        self.env["stock.picking.to.batch"].with_context(
            active_ids=self.pickings.ids
        ).create(
            {
                "mode": "new",
                "batch_by_group": True,
                "group_field_ids": False,
            }
        ).attach_pickings()
        self.assertEqual(len(self.pickings.mapped("batch_id")), 1)

    def test_sptb_new_batch_groupby_fields(self):
        """Add picking to new batch and group by fields"""
        field_origin = self.env.ref("stock.field_stock_picking__origin")
        field_scheduled_date = self.env.ref("stock.field_stock_picking__scheduled_date")
        self.pickings.batch_id = self.batch
        wizard = (
            self.env["stock.picking.to.batch"]
            .with_context(active_ids=self.pickings.ids)
            .create(
                {
                    "mode": "new",
                    "batch_by_group": True,
                    "group_field_ids": [
                        (0, 0, {"field_id": field_origin.id}),
                        (0, 0, {"field_id": field_scheduled_date.id}),
                    ],
                }
            )
        )
        with self.assertRaises(UserError):
            wizard.attach_pickings()
        self.pickings.batch_id = False
        wizard.attach_pickings()
        self.assertEqual(len(self.pickings.mapped("batch_id")), 2)
