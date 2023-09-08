# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockLocation(models.Model):

    _inherit = "stock.location"

    is_considered_as_source = fields.Boolean(
        index=True,
        compute="_compute_is_considered_as_source",
        store=True,
        readonly=False,
        help="Check this to consider this picking type as the source one for "
        "the moves later in the flow.",
    )

    @api.depends("is_zone")
    def _compute_is_considered_as_source(self):
        # Reset value if is_zone field is set to False
        self.filtered(lambda location: location.is_zone).update(
            {"is_considered_as_source": False}
        )
