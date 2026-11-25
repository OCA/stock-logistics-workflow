# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class StockShipmentComposerWizardLine(models.TransientModel):
    _name = "stock.shipment.composer.wizard.line"
    _description = "Wizard Line for Shipment Composer"
    _inherit = "stock.shipment.composer.line.mixin"

    wizard_id = fields.Many2one("stock.shipment.composer.wizard")
    quantity = fields.Float(compute="_compute_quantity", store=True, readonly=False)
    product_uom_qty = fields.Float(related="move_id.product_uom_qty")
    uom_id = fields.Many2one(related="move_id.product_uom", string="UoM")
    remarks = fields.Text()

    @api.depends("move_id")
    def _compute_quantity(self):
        for rec in self:
            rec.quantity = rec.move_id.composer_unallocated_qty
