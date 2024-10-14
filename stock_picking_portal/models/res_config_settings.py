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
        super().set_values()
        ICPSudo = self.env["ir.config_parameter"].sudo()
        ICPSudo.set_param(
            "stock_picking_portal.portal_visible_operation_ids",
            ",".join(str(i) for i in self.portal_visible_operation_ids.ids),
        )
        return

    @api.model
    def get_values(self):
        res = super().get_values()
        ICPSudo = self.env["ir.config_parameter"].sudo()
        portal_visible_operation_ids = ICPSudo.get_param(
            "stock_picking_portal.portal_visible_operation_ids", default=False
        )
        if portal_visible_operation_ids:
            res.update(
                portal_visible_operation_ids=[
                    int(r) for r in portal_visible_operation_ids.split(",")
                ]
            )
        return res
