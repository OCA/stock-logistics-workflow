# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command, api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    portal_visible_operation_ids = fields.Many2many(
        comodel_name="stock.picking.type",
        string="Portal Visible Operations",
    )

    def set_values(self):
        res = super().set_values()
        selected = self.portal_visible_operation_ids
        currently_visible = self.env["stock.picking.type"].search(
            [("portal_visible", "=", True)]
        )

        (currently_visible - selected).write({"portal_visible": False})
        (selected - currently_visible).write({"portal_visible": True})
        return res

    @api.model
    def get_values(self):
        res = super().get_values()
        visible_ids = (
            self.env["stock.picking.type"].search([("portal_visible", "=", True)]).ids
        )
        res.update(
            {
                "portal_visible_operation_ids": [Command.set(visible_ids)],
            }
        )
        return res
