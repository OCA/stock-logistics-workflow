# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    portal_visible_operation_ids = fields.Many2many(
        comodel_name="stock.picking.type",
        string="Portal Visible Operations",
    )

    def set_values(self):
        """Save the M2M into the boolean field on stock.picking.type,
        updating only the records whose flag have changed."""
        res = super().set_values()
        selected = self.portal_visible_operation_ids
        currently_visible = self.env["stock.picking.type"].search(
            [
                ("portal_visible", "=", True),
            ],
        )

        to_invisible = currently_visible - selected
        to_visible = selected - currently_visible

        if to_invisible:
            to_invisible.write({"portal_visible": False})
        if to_visible:
            to_visible.write({"portal_visible": True})

        return res

    @api.model
    def get_values(self):
        res = super().get_values()
        visible_ids = (
            self.env["stock.picking.type"]
            .search(
                [
                    ("portal_visible", "=", True),
                ],
            )
            .ids
        )
        res.update(portal_visible_operation_ids=visible_ids)
        return res
