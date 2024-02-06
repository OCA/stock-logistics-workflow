# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class StockPickingToBatchGroupField(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Product = cls.env["product.product"]
        cls.picking_model = cls.env["stock.picking"]
        cls.batch_model = cls.env["stock.picking.batch"]
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.stock_loc = cls.env.ref("stock.stock_location_stock")
        cls.customer_loc = cls.env.ref("stock.stock_location_customers")
        cls.productA = cls.Product.create({"name": "Product A", "type": "consu"})
        cls.productB = cls.Product.create({"name": "Product A", "type": "product"})
        cls.pickingA = cls.picking_model.with_context(planned=True).create(
            {
                "picking_type_id": cls.picking_type_out.id,
                "location_id": cls.stock_loc.id,
                "location_dest_id": cls.customer_loc.id,
                "origin": "A",
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test move",
                            "product_id": cls.productA.id,
                            "product_uom_qty": 1,
                            "location_id": cls.stock_loc.id,
                            "location_dest_id": cls.customer_loc.id,
                        },
                    )
                ],
            }
        )
        cls.pickingB = cls.picking_model.with_context(planned=True).create(
            {
                "picking_type_id": cls.picking_type_out.id,
                "location_id": cls.stock_loc.id,
                "location_dest_id": cls.customer_loc.id,
                "origin": "B",
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test move",
                            "product_id": cls.productB.id,
                            "product_uom_qty": 1,
                            "location_id": cls.stock_loc.id,
                            "location_dest_id": cls.customer_loc.id,
                        },
                    )
                ],
            }
        )
        cls.pickings = cls.pickingA + cls.pickingB
        cls.batch = cls.batch_model.create({})

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
