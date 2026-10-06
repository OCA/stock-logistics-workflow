# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class StockShipmentComposerLine(models.Model):
    _name = "stock.shipment.composer.line"
    _description = "Stock Shipment Composer Line"

    composer_id = fields.Many2one(
        "stock.shipment.composer", required=True, ondelete="cascade"
    )
    move_id = fields.Many2one("stock.move", required=True)
    picking_id = fields.Many2one(related="move_id.picking_id", string="Transfer")
    quantity = fields.Float(compute="_compute_quantity", store=True, readonly=False)
    product_uom_qty = fields.Float(related="move_id.product_uom_qty")
    reserved_availability = fields.Float(
        compute="_compute_reserved_availability",
        string="Reserved",
    )
    quantity_done = fields.Float(
        compute="_compute_quantity_done",
        string="Done",
    )
    uom_id = fields.Many2one(related="move_id.product_uom", string="UoM")
    move_state = fields.Selection(related="move_id.state", string="Move Status")
    remarks = fields.Text()
    state = fields.Selection(related="composer_id.state", store=True)
    reserved_enough = fields.Boolean(compute="_compute_reserved_enough")
    location_id = fields.Many2one(
        related="move_id.location_id", string="Source Location"
    )
    location_dest_id = fields.Many2one(
        related="move_id.location_dest_id", string="Destination Location"
    )

    @api.depends("move_id.quantity", "move_id.picked", "move_id.state")
    def _compute_reserved_availability(self):
        for rec in self:
            move = rec.move_id
            if move.state == "done" or move.picked:
                rec.reserved_availability = 0.0
            else:
                rec.reserved_availability = move.quantity

    @api.depends("move_id.quantity", "move_id.picked", "move_id.state")
    def _compute_quantity_done(self):
        for rec in self:
            move = rec.move_id
            if move.state == "done" or move.picked:
                rec.quantity_done = move.quantity
            else:
                rec.quantity_done = 0.0

    @api.depends("move_id")
    def _compute_quantity(self):
        for rec in self:
            rec.quantity = rec.move_id.composer_unallocated_qty

    @api.depends("quantity", "reserved_availability")
    def _compute_reserved_enough(self):
        for rec in self:
            rec.reserved_enough = rec.reserved_availability >= rec.quantity

    def action_product_forecast_report(self):
        self.ensure_one()
        return self.move_id.action_product_forecast_report()

    def action_show_details(self):
        self.ensure_one()
        return self.move_id.action_show_details()
