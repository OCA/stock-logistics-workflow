# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPick(models.Model):
    _name = "stock.picking"
    _inherit = ["portal.mixin", "stock.picking"]

    signed_by = fields.Char(copy=False)
    signed_on = fields.Datetime(copy=False)

    def _compute_access_url(self):
        super()._compute_access_url()
        for picking in self:
            picking.access_url = f"/my/stock_operations/{picking.id}"
        return

    def _get_report_base_filename(self):
        self.ensure_one()
        return f"{self.picking_type_id.name} {self.name}"
