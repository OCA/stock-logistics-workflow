# Copyright 2024 Akretion France (http://www.akretion.com/)
# @author: Mathieu Delva <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    show_force_quantity = fields.Boolean(compute="_compute_show_force_quantity")
    qty_in_stock = fields.Float(compute="_compute_qty_in_stock")
    picking_state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], related='picking_id.state', string="Picking Status")

    def _compute_show_force_quantity(self):
        for record in self:
            record.show_force_quantity = False
            if record.forecast_availability < record.product_uom_qty:
                record.show_force_quantity = True

    def _compute_qty_in_stock(self):
        for record in self:
            record.qty_in_stock = record.product_id.with_context(warehouse=record.location_id.get_warehouse().id).qty_available
    
    def force_quantity(self):
        self.ensure_one()
        
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock_move_force_reservation.stock_move_force_reservation_action"
        )
        self.env.context = dict(self.env.context)
        self.env.context.update({"product_id": self.product_id})
        action.update(
            {   
                "active_id": self.id,
                "active_model": self._name,       
            }
        )
        return action