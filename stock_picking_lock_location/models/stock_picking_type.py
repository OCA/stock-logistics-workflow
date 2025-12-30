# Copyright (C) 2025 Akretion (<http://www.akretion.com>).
# @author Mathieu Delva <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    company_lock_location_id = fields.Boolean(
        string="Company Lock Location", related="company_id.lock_location_id"
    )
    lock_location_id = fields.Boolean(
        string="Lock Source Location",
        compute="_compute_lock_location_id",
        readonly=False,
        store=True,
    )
    company_lock_location_dest_id = fields.Boolean(
        string="Company Lock Destination Location",
        related="company_id.lock_location_dest_id",
    )
    lock_location_dest_id = fields.Boolean(
        string="Lock Destination Location",
        compute="_compute_lock_location_dest_id",
        readonly=False,
        store=True,
    )

    @api.depends("code", "company_id.lock_location_id")
    def _compute_lock_location_id(self):
        for record in self:
            record.lock_location_id = (
                True
                if record.code in ["incoming", "outgoing"]
                and record.company_lock_location_id
                else False
            )

    @api.depends("code", "company_id.lock_location_dest_id")
    def _compute_lock_location_dest_id(self):
        for record in self:
            record.lock_location_dest_id = (
                True
                if record.code in ["incoming", "outgoing"]
                and record.company_lock_location_dest_id
                else False
            )
