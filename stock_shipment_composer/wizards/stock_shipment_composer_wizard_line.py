# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class StockShipmentComposerWizardLine(models.TransientModel):
    _name = "stock.shipment.composer.wizard.line"
    _description = "Wizard Line for Shipment Composer"

    wizard_id = fields.Many2one("stock.shipment.composer.wizard")
    move_id = fields.Many2one("stock.move", required=True)
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
    remarks = fields.Text()

    @api.depends("move_id")
    def _compute_quantity(self):
        for rec in self:
            rec.quantity = rec.move_id.composer_unallocated_qty

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
