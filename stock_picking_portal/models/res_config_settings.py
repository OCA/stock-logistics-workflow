# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    portal_visible_operation_ids = fields.Many2many(
        comodel_name="stock.picking.type",
        string="Portal Visible Operations",
    )

    @api.model
    def get_values(self):
        res = super().get_values()
        visible = self.env["stock.picking.type"].search([("portal_visible", "=", True)])
        res.update(portal_visible_operation_ids=visible.ids)
        return res

    def set_values(self):
        res = super().set_values()
        all_types = self.env["stock.picking.type"].search([])
        all_types.write({"portal_visible": False})
        self.portal_visible_operation_ids.write({"portal_visible": True})
        return res
