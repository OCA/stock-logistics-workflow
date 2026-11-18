# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class StockShipmentComposerLineMixin(models.AbstractModel):
    _name = "stock.shipment.composer.line.mixin"
    _description = "Stock Shipment Composer Line Mixin"

    move_id = fields.Many2one("stock.move", required=True)
    reserved_availability = fields.Float(related="move_id.reserved_availability")
    quantity_done = fields.Float(related="move_id.quantity_done")
