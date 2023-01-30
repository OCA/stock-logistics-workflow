# Copyright 2023 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    @api.constrains("resupply_wh_ids", "reception_steps")
    def _check_resupply_and_steps(self):
        for rec in self:
            if rec.resupply_wh_ids and rec.reception_steps == "one_step":
                raise ValidationError(
                    _(
                        "The receipt of goods must be done in 2 steps"
                        "in order to be able to make replenishments via a "
                        "another warehouse of the company."
                    )
                )
