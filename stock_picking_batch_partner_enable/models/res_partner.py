# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    allow_batch_grouping = fields.Boolean(
        string="Allowed for Automatic Batch grouping",
        default=True,
        help="If disabled, pickings for this partner will not be automatically grouped "
        " into batches, even when the operation type has 'Automatic Batches' enabled.",
    )

    @api.model
    def _commercial_fields(self):
        return super()._commercial_fields() + ["allow_batch_grouping"]
