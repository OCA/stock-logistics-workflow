# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo_test_helper import FakeModelLoader


class PutawayHookCommon:
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .model import StockLocation, StockPutawayRule

        cls.loader.update_registry((StockPutawayRule,))
        cls.loader.update_registry((StockLocation,))
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product",
            }
        )
        cls.location_internal_1 = cls.env["stock.location"].create(
            {
                "name": "Internal for putaways",
                "usage": "internal",
            }
        )
        cls.location_internal_2 = cls.env["stock.location"].create(
            {
                "name": "Internal 2 for putaways",
                "usage": "internal",
            }
        )
        cls.location_internal_parent_3 = cls.env["stock.location"].create(
            {
                "name": "Parent 3 for putaways",
                "usage": "internal",
            }
        )
        cls.location_internal_shelf_3 = cls.env["stock.location"].create(
            {
                "name": "Shelf 3 for putaways",
                "usage": "internal",
                "location_id": cls.location_internal_parent_3.id,
            }
        )
        cls.location_internal_3 = cls.env["stock.location"].create(
            {
                "name": "Internal 3 for putaways",
                "usage": "internal",
                "location_id": cls.location_internal_parent_3.id,
            }
        )

        cls.env["stock.putaway.rule"].create(
            {
                "foo": True,  # The field that is passed through context
                "location_in_id": cls.location_internal_parent_3.id,
                "location_out_id": cls.location_internal_shelf_3.id,
            }
        )

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()
