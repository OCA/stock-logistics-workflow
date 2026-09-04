# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    portal_visible = fields.Boolean(
        string="Visible in Portal",
        default=False,
        help="If checked, pickings of this type will be shown in the customer portal.",
    )

    @api.model
    def _get_available_operations(self):
        return self.search([("portal_visible", "=", True)]).ids
