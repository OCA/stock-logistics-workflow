# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class StockScrap(models.Model):
    _inherit = "stock.scrap"

    scrap_reason_required = fields.Boolean(compute="_compute_scrap_reason_required")

    # Depend on scrap_qty to make its value triggered when onchange
    @api.depends("scrap_qty")
    def _compute_scrap_reason_required(self):
        icp_sudo = self.env["ir.config_parameter"].sudo()
        scrap_reason_required = safe_eval(
            icp_sudo.get_param("scrap_order.scrap_reason_required", "False")
        )
        for rec in self:
            rec.scrap_reason_required = scrap_reason_required
