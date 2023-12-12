# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    disable_picking_grouping = fields.Boolean(
        string="Do not group deliveries",
        default=False,
    )

    @api.model
    def _commercial_fields(self):
        return super()._commercial_fields() + ["disable_picking_grouping"]
