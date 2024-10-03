# Copyright 2024 360ERP (<https://www.360erp.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.mrp.tests.common import TestMrpCommon


class TestStockScrapTierValidationMrp(TestMrpCommon):
    def test_stock_scrap_tier_validation_mrp(self):
        """Scrapping from mrp objectsdoes not open in a popup"""
        bom = self.env["mrp.bom"].create(
            {
                "product_id": self.product_6.id,
                "product_tmpl_id": self.product_6.product_tmpl_id.id,
                "product_qty": 1,
                "product_uom_id": self.product_6.uom_id.id,
                "type": "normal",
                "bom_line_ids": [
                    (0, 0, {"product_id": self.product_2.id, "product_qty": 2.03}),
                    (0, 0, {"product_id": self.product_8.id, "product_qty": 4.16}),
                ],
                "operation_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Gift Wrap Maching",
                            "workcenter_id": self.workcenter_1.id,
                            "time_cycle": 15,
                            "sequence": 1,
                        },
                    ),
                ],
            }
        )
        production = self.env["mrp.production"].create(
            {
                "product_id": self.product_6.id,
                "bom_id": bom.id,
                "product_qty": 1,
                "product_uom_id": self.product_6.uom_id.id,
            }
        )

        # Scrap from mrp.production
        mo_action = production.button_scrap()
        self.assertFalse(mo_action.get("target"))

        # Scrap from mrp.workorder
        wo_action = production.workorder_ids[0].button_scrap()
        self.assertFalse(wo_action.get("target"))
