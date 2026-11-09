# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class StockShipmentComposerLineMixin(models.AbstractModel):
    _name = "stock.shipment.composer.line.mixin"
    _description = "Stock Shipment Composer Line Mixin"

    move_id = fields.Many2one("stock.move", required=True)
    reserved_availability = fields.Float(
        compute="_compute_reserved_availability",
        string="Reserved",
    )
    quantity_done = fields.Float(
        compute="_compute_quantity_done",
        string="Done",
    )

    @api.depends("move_id.quantity", "move_id.state")
    def _compute_reserved_availability(self):
        for rec in self:
            move = rec.move_id
            rec.reserved_availability = 0.0 if move.state == "done" else move.quantity

    @api.depends("move_id.quantity", "move_id.picked", "move_id.state")
    def _compute_quantity_done(self):
        for rec in self:
            move = rec.move_id
            if move.state == "done" or move.picked:
                rec.quantity_done = move.quantity
            else:
                rec.quantity_done = 0.0
