# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from werkzeug import urls

from odoo import api, fields, models


class PickingLinkWizard(models.TransientModel):
    _name = "picking.link.wizard"
    _description = "Generate signature link"

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        res_id = self.env.context.get("active_id")
        res_model = self.env.context.get("active_model")
        if res_id and res_model:
            res.update({"res_model": res_model, "res_id": res_id})
        return res

    picking_id = fields.Many2one(
        "stock.picking",
        string="Picking",
        default=lambda self: self.env.context.get("active_id"),
    )
    link = fields.Char(string="Signature link", compute="_compute_link")

    @api.depends("picking_id")
    def _compute_link(self):
        """Generate signature link"""
        for picking_link in self:
            picking = picking_link.picking_id
            base_url = picking.get_base_url()
            picking._portal_ensure_token()
            picking._compute_access_url()
            url_params = {
                "access_token": picking.access_token,
            }
            picking_link.link = (
                f"{base_url}{picking.access_url}?{urls.url_encode(url_params)}"
            )
