from odoo import fields, models


class StockPickingAlertWizard(models.TransientModel):
    _name = "stock.picking.alert.wizard"
    _description = "Stock Picking Alert Wizard"

    picking_id = fields.Many2one(comodel_name="stock.picking", required=True)

    def action_confirm(self):
        self.ensure_one()
        return self.picking_id.with_context(bypass_alert=True).button_validate()
