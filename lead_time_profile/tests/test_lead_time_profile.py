# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo_test_helper import FakeModelLoader

from odoo.tests import TransactionCase


class TestLeadTimeProfile(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .test_models import TestLeadTimeProfile

        cls.loader.update_registry((TestLeadTimeProfile,))
        cls.country = cls.env.ref("base.us")
        cls.state = cls.env.ref("base.state_us_1")
        cls.company = cls.env.company
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "state_id": cls.state.id,
                "country_id": cls.country.id,
            }
        )
        cls.warehouse = cls.env["stock.warehouse"].create(
            {
                "name": "Test Warehouse",
                "code": "TWH",
            }
        )
        cls.other_warehouse = cls.env["stock.warehouse"].create(
            {
                "name": "Other Warehouse",
                "code": "OTH",
            }
        )
        cls.test_model = cls.env.ref("lead_time_profile.model_test_lead_time_profile")
        cls.profile_exact = cls.env["lead.time.profile"].create(
            {
                "warehouse_id": cls.warehouse.id,
                "partner_id": cls.partner.id,
                "state_id": cls.state.id,
                "country_id": cls.country.id,
                "company_id": cls.company.id,
                "model_id": cls.test_model.id,
                "lead_time": 4,
            }
        )
        cls.profile_state_level = cls.env["lead.time.profile"].create(
            {
                "warehouse_id": cls.warehouse.id,
                "partner_id": False,
                "state_id": cls.state.id,
                "country_id": cls.country.id,
                "company_id": cls.company.id,
                "model_id": cls.test_model.id,
                "lead_time": 3,
            }
        )
        cls.profile_country_level = cls.env["lead.time.profile"].create(
            {
                "warehouse_id": cls.warehouse.id,
                "partner_id": False,
                "state_id": False,
                "country_id": cls.country.id,
                "company_id": cls.company.id,
                "model_id": cls.test_model.id,
                "lead_time": 2,
            }
        )

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    def create_test_record(self, partner, warehouse):
        record = self.env["test.lead.time.profile"].create(
            {
                "name": "Test Case",
                "partner_id": partner.id,
                "warehouse_id": warehouse.id,
            }
        )
        record._compute_delivery_lead_time()
        return record

    def test_exact_match(self):
        record = self.create_test_record(self.partner, self.warehouse)
        self.assertEqual(record.delivery_lead_time, 4, "Should match exact profile")

    def test_state_level_fallback(self):
        partner = self.env["res.partner"].create(
            {
                "name": "Only State Match",
                "state_id": self.state.id,
                "country_id": self.country.id,
            }
        )
        record = self.create_test_record(partner, self.warehouse)
        self.assertEqual(
            record.delivery_lead_time, 3, "Should fallback to state-level profile"
        )

    def test_country_level_fallback(self):
        partner = self.env["res.partner"].create(
            {
                "name": "Only Country Match",
                "state_id": False,
                "country_id": self.country.id,
            }
        )
        record = self.create_test_record(partner, self.warehouse)
        self.assertEqual(
            record.delivery_lead_time, 2, "Should fallback to country-level profile"
        )

    def test_warehouse_mismatch(self):
        partner = self.env["res.partner"].create(
            {
                "name": "Warehouse Mismatch",
                "state_id": self.state.id,
                "country_id": self.country.id,
            }
        )
        record = self.create_test_record(partner, self.other_warehouse)
        self.assertEqual(
            record.delivery_lead_time, 0, "Should not match due to warehouse mismatch"
        )

    def test_partner_no_match(self):
        partner = self.env["res.partner"].create(
            {
                "name": "No Match",
                "state_id": False,
                "country_id": False,
            }
        )
        record = self.create_test_record(partner, self.other_warehouse)
        self.assertEqual(record.delivery_lead_time, 0, "Should not match any profile")
