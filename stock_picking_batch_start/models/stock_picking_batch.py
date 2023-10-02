# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPickingBatch(models.Model):
    _inherit = "stock.picking.batch"

    action_start_allowed = fields.Boolean(compute="_compute_action_start_allowed")
    action_cancel_start_allowed = fields.Boolean(
        compute="_compute_action_cancel_start_allowed"
    )
    started = fields.Boolean(compute="_compute_started", store=True)

    @api.depends("picking_ids", "picking_ids.action_start_allowed")
    def _compute_action_start_allowed(self):
        for batch in self:
            allowed = False
            if batch.picking_ids:
                allowed = all(batch.mapped("picking_ids.action_start_allowed"))
            batch.action_start_allowed = allowed

    @api.depends("picking_ids", "picking_ids.action_cancel_start_allowed")
    def _compute_action_cancel_start_allowed(self):
        for batch in self:
            allowed = False
            if batch.picking_ids:
                allowed = all(batch.mapped("picking_ids.action_cancel_start_allowed"))
            batch.action_cancel_start_allowed = allowed

    @api.depends("picking_ids", "picking_ids.started")
    def _compute_started(self):
        for batch in self:
            started = False
            if batch.picking_ids:
                started = batch.picking_ids and all(batch.mapped("picking_ids.started"))
            batch.started = started

    def action_start(self):
        self.picking_ids.action_start()

    def action_cancel_start(self):
        self.picking_ids.action_cancel_start()
