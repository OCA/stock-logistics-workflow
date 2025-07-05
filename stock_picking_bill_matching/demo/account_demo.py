# Copyright 2026 Akretion (https://www.akretion.com).
# @author Raphaël Valyi <raphael.valyi@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import time

from odoo import Command, api, models


class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"

    @api.model
    def _get_demo_data(self):
        """Yield the standard demo data, then yield our module's demo bills."""
        yield from super()._get_demo_data()
        yield self._get_stock_picking_bill_matching_demo_move()

    @api.model
    def _get_stock_picking_bill_matching_demo_move(self):
        cid = self.env.company.id
        ref = self.env.ref
        return (
            "account.move",
            {
                f"{cid}_demo_bill_matching_1": {
                    "move_type": "in_invoice",
                    "partner_id": ref("base.res_partner_1").id,
                    "invoice_date": time.strftime("%Y-%m-%d"),
                    "invoice_line_ids": [
                        Command.create(
                            {
                                "product_id": ref("product.product_delivery_01").id,
                                "quantity": 10,
                                "price_unit": 50.0,
                            }
                        ),
                        Command.create(
                            {
                                "product_id": ref("product.product_product_25").id,
                                "quantity": 5,
                                "price_unit": 100.0,
                            }
                        ),
                    ],
                }
            },
        )
