from odoo import Command, api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    portal_visible_operation_ids = fields.Many2many(
        "stock.picking.type", string="Portal Visible Operations"
    )

    def set_values(self):
        res = super().set_values()
        selected = self.portal_visible_operation_ids
        current = self.env["stock.picking.type"].search([("portal_visible", "=", True)])
        (current - selected).write({"portal_visible": False})
        (selected - current).write({"portal_visible": True})
        return res

    @api.model
    def get_values(self):
        res = super().get_values()
        visible = (
            self.env["stock.picking.type"].search([("portal_visible", "=", True)]).ids
        )
        res.update({"portal_visible_operation_ids": [Command.set(visible)]})
        return res
