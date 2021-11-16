# Copyright 2021 Camptocamp (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

from odoo.tests.common import SavepointCase


@freeze_time("2021-11-15 08:00:00")
class TestMassScrap(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        # Warehouse.
        cls.warehouse_1 = cls.env["stock.warehouse"].create(
            {"name": "Test Warehouse 1", "code": "WA1"}
        )

        # Locations.
        cls.location_stock = cls.env.ref("stock.stock_location_stock")
        cls.location_scrap = cls.env["stock.location"].search(
            [("scrap_location", "=", True)], limit=1
        )

        # Products.
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "product",
                "use_expiration_date": True,
                "tracking": "lot",
            }
        )

        # Lots
        cls.lot_01 = cls._create_lot(
            name="Lot 01", expiration_date="2021-11-18 07:50:00"
        )
        cls.lot_02 = cls._create_lot(
            name="Lot 02", expiration_date="2021-11-20 14:10:00"
        )

    @classmethod
    def _create_lot(cls, name, expiration_date):
        lot = cls.env["stock.production.lot"].create(
            {
                "name": name,
                "product_id": cls.product.id,
                "company_id": cls.env.user.company_id.id,
                "expiration_date": expiration_date,
            }
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.location_stock, 1, lot_id=lot
        )
        return lot

    def _create_wizard(self, date_expiration_to_scrap, specific_warehouse_id):
        return self.env["mass.scrap"].create(
            {
                "date_expiration_to_scrap": date_expiration_to_scrap,
                "specific_warehouse_id": specific_warehouse_id,
            }
        )

    def _get_quants_to_scrap(
        self, date_expiration_to_scrap, specific_warehouse_id=False
    ):
        wizard = self._create_wizard(date_expiration_to_scrap, specific_warehouse_id)
        wizard.onchange_quants_to_scrap()
        return wizard.stock_quant_ids

    def _run_wizard(self, date_expiration_to_scrap):
        wizard = self._create_wizard(date_expiration_to_scrap, False)
        wizard.button_confirm()

    def _get_scrap(self):
        return self.env["stock.scrap"].search([], order="id")

    def test_quants_selection(self):
        """
        Rule for quants selection are:
        * location usage must be internal
        * expiration date must be lower than chosen
        * location must be under chosen warehouse

        Data for this test:
        * Lot 01 expiration date: 2021-11-18 07:50:00
        * Lot 02 expiration date: 2021-11-20 14:10:00
        """

        # Date: 2021-11-15 12:00:00
        quants = self._get_quants_to_scrap(
            date_expiration_to_scrap="2021-11-15 12:00:00"
        )
        # ==> No quants selected as expiration is in the future.
        self.assertEqual(len(quants), 0)

        # Date: 2021-11-18 07:49:00
        quants = self._get_quants_to_scrap(
            date_expiration_to_scrap="2021-11-18 07:49:00"
        )
        # ==> No quants selected as expiration is in the future.
        self.assertEqual(len(quants), 0)

        # Date: 2021-11-18 07:51:00
        quants = self._get_quants_to_scrap(
            date_expiration_to_scrap="2021-11-18 07:51:00"
        )
        # ==> First lot must be scrap
        self.assertEqual(len(quants), 1)

        # Date: 2021-11-22 11:30:00
        quants = self._get_quants_to_scrap(
            date_expiration_to_scrap="2021-11-22 11:30:00"
        )
        # ==> Both lot must be scrap
        self.assertEqual(len(quants), 2)

        # Check on other warehouse
        quants = self._get_quants_to_scrap(
            date_expiration_to_scrap="2021-11-22 11:30:00",
            specific_warehouse_id=self.warehouse_1.id,
        )
        # ==> No quants selected as on another warehouse
        self.assertEqual(len(quants), 0)

        # Move lot 1 on other warehouse
        self.lot_01.quant_ids.location_id = self.warehouse_1.lot_stock_id
        quants = self._get_quants_to_scrap(
            date_expiration_to_scrap="2021-11-22 11:30:00",
            specific_warehouse_id=self.warehouse_1.id,
        )
        # ==> First lot must be scrap because on wanted warehouse
        self.assertEqual(len(quants), 1)

        # Change location usage to non-internal
        self.lot_01.quant_ids.location_id.usage = "transit"
        quants = self._get_quants_to_scrap(
            date_expiration_to_scrap="2021-11-22 11:30:00",
            specific_warehouse_id=self.warehouse_1.id,
        )
        # ==> No quants selected as on non internal location
        self.assertEqual(len(quants), 0)

    def test_scrap(self):
        """
        For each quant to scrap, we create a product scrap.
        If validate scraps, quants have no remaining quantity.

        Data for this test:
        * Lot 01 expiration date: 2021-11-18 07:50:00
        * Lot 02 expiration date: 2021-11-20 14:10:00
        """

        date = "2021-11-22 11:30:00"

        # Get quants
        quants = self._get_quants_to_scrap(date_expiration_to_scrap=date)
        self.assertEqual(len(quants), 2)

        # Create scraps
        existing_scraps = self._get_scrap()
        self._run_wizard(date)
        scraps = self._get_scrap() - existing_scraps

        # A scrap must have created for both lots
        self.assertEqual(len(scraps), 2)

        for i in range(0, 1):
            self.assertEqual(scraps[i].product_id, quants[i].product_id)
            self.assertEqual(scraps[i].lot_id, quants[i].lot_id)
            self.assertEqual(scraps[i].scrap_qty, quants[i].quantity)
            self.assertEqual(scraps[i].product_uom_id, quants[i].product_uom_id)
            self.assertEqual(scraps[i].location_id, quants[i].location_id)
            self.assertEqual(scraps[i].scrap_location_id, self.location_scrap)
            self.assertEqual(scraps[i].state, "draft")

        # Create scrap no change quants to scrap, because still in draft
        quants = self._get_quants_to_scrap(date_expiration_to_scrap=date)
        self.assertEqual(len(quants), 2)
        for quant in quants:
            self.assertEqual(quant.quantity, 1)

        # Validate scrap
        self.env["stock.scrap"].with_context(active_ids=scraps.ids).mass_validate()
        for scrap in scraps:
            self.assertEqual(scrap.state, "done")
        for quant in quants:
            self.assertEqual(quant.quantity, 0)

        # No remaining quants to scrap now we really done the scrap
        quants = self._get_quants_to_scrap(date_expiration_to_scrap=date)
        self.assertEqual(len(quants), 0)
