# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPick(models.Model):
    _name = "stock.picking"
    _inherit = ["portal.mixin", "stock.picking"]

    signed_by = fields.Char(copy=False)
    signed_on = fields.Datetime(copy=False)
    signature = fields.Binary(copy=False)
    is_signed = fields.Boolean(compute="_compute_is_signed", store=False)
    access_url = fields.Char(compute="_compute_access_url", string="Portal Access URL")

    def _compute_is_signed(self):
        for p in self:
            p.is_signed = bool(p.signature)

    @api.model
    def _get_available_operations(self):
        picking_types = (
            self.env["stock.picking.type"]
            .sudo()
            .search(
                [
                    ("portal_visible", "=", True),
                    ("company_id", "in", [False, self.env.company.id]),
                ]
            )
        )
        return picking_types.ids

    def _compute_access_url(self):
        res = super()._compute_access_url()
        for picking in self:
            picking.access_url = "/my/stock_operations/%s" % (picking.id)
        return res

    def _get_report_base_filename(self):
        self.ensure_one()
        return f"{self.picking_type_id.name} {self.name}"
