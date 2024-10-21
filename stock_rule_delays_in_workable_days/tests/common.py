# Copyright 2024 Foodles (https://www.foodles.co/).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo.tests.common import SavepointCase

from ..models.weekday import WeekdaysEnum


class CommonStockPurchaseOrderDateRule(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.delta_days_merge = 0
        cls.env["ir.config_parameter"].sudo().set_param(
            "purchase_stock.delta_days_merge", cls.delta_days_merge
        )

        cls.company_id = cls.env.ref("base.main_company")

        cls.lead_times_by_day_value_2 = cls.env.ref(
            "stock_rule_delays_in_workable_days.lead_times_by_day_value_2"
        )
        cls.lead_times_by_day_value_10 = cls.env.ref(
            "stock_rule_delays_in_workable_days.lead_times_by_day_value_10"
        )
        cls.lead_times_by_day_value_11 = cls.env.ref(
            "stock_rule_delays_in_workable_days.lead_times_by_day_value_11"
        )
        cls.lead_times_by_day_value_12 = cls.env.ref(
            "stock_rule_delays_in_workable_days.lead_times_by_day_value_12"
        )
        cls.lead_times_by_day_value_14 = cls.env.ref(
            "stock_rule_delays_in_workable_days.lead_times_by_day_value_14"
        )
        cls.lead_times_by_day_value_15 = cls.env.ref(
            "stock_rule_delays_in_workable_days.lead_times_by_day_value_15"
        )
        cls.lead_times_by_day_value_16 = cls.env.ref(
            "stock_rule_delays_in_workable_days.lead_times_by_day_value_16"
        )

        cls.partner_customer = cls.env["res.partner"].create(
            {
                "name": "Test Customer",
            }
        )

        cls.partner_supplier = cls.env["res.partner"].create(
            {
                "name": "Test Supplier",
            }
        )

        cls.template_id = cls.env["product.template"].create(
            {
                "name": "Test Product Template",
                "type": "product",
                "purchase_method": "purchase",
                "tracking": "lot",
                "use_expiration_date": True,
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "name": cls.partner_supplier.id,
                            "price": 10,
                        },
                    )
                ],
            }
        )
        cls.product_id = cls.template_id.product_variant_id

        cls.purchase_order_id = cls.env["purchase.order"].create(
            {
                "partner_id": cls.env["res.partner"]
                .create(
                    {
                        "name": "Test Partner",
                    }
                )
                .id,
                "company_id": cls.company_id.id,
            }
        )

        cls.picking_type_in = cls.env.ref("stock.picking_type_in")

        #    Stock warehouse

        cls.stock_warehouse = cls.env["stock.warehouse"].create(
            {
                "name": "Test Warehouse",
                "code": "TEST",
                "company_id": cls.company_id.id,
                "calendar_id": cls.env["resource.calendar"]
                .create(
                    {
                        "name": "Test Calendar",
                    }
                )
                .id,
            }
        )

        #    Stock Location

        cls.stock_supplier_location = cls.env["stock.location"].create(
            {
                "name": "Supplier Location",
                "usage": "supplier",
                "company_id": cls.company_id.id,
            }
        )

        cls.stock_receipt_location = cls.env["stock.location"].create(
            {
                "name": "Receipt Location",
                "usage": "internal",
                "company_id": cls.company_id.id,
                "warehouse_id": cls.stock_warehouse.id,
            }
        )

        cls.stock_rule = cls.env["stock.rule"].create(
            {
                "name": "Test Stock Rule",
                "location_src_id": cls.env.ref("stock.stock_location_stock").id,
                "location_id": cls.env.ref("stock.stock_location_customers").id,
                "action": "buy",
                "route_id": cls.env.ref("stock.route_warehouse0_mto").id,
                "company_id": cls.env.ref("base.main_company").id,
                "picking_type_id": cls.picking_type_in.id,
                "lead_times_by_day_ids": [
                    (
                        0,
                        0,
                        {
                            "weekday": WeekdaysEnum.Tuesday.value,
                            "value_ids": [
                                (
                                    6,
                                    0,
                                    cls.lead_times_by_day_value_12.ids,
                                ),  # Sunday (W+1)
                                (
                                    6,
                                    0,
                                    cls.lead_times_by_day_value_14.ids,
                                ),  # Tuesday (W+2)
                            ],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "weekday": WeekdaysEnum.Friday.value,
                            "value_ids": [
                                (
                                    6,
                                    0,
                                    cls.lead_times_by_day_value_10.ids,
                                ),  # Monday (W+1)
                            ],
                        },
                    ),
                ],
            }
        )
