# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)
                    
class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def _get_carrier_type_selection(self):
        carrier_obj = self.env['delivery.carrier']
        return carrier_obj._get_carrier_type_selection()

    carrier_id = fields.Many2one(
        comodel_name='delivery.carrier',
        string='Carrier',
        states={'done': [('readonly', True)]},
    )
    carrier_type = fields.Selection(
        related='carrier_id.carrier_type',
        string='Carrier type',
        readonly=True,
    )
    shipping_expedition_id = fields.Many2one(
        comodel_name='shipping.expedition',
        inverse_name='picking_id',
        string='Expedition',
        readonly=True,
        copy=False
    )
    shipping_expedition_note = fields.Text(
        string='Expedition note',
    )
    
    @api.multi
    def action_cancel(self):
        return_action_cancel = super(StockPicking, self).action_cancel()
        #operations
        for obj in self:
            if obj.shipping_expedition_id.id>0:
                obj.shipping_expedition_id.state = 'canceled'
        #return
        return return_action_cancel

    @api.multi
    def get_shipping_expedition_values(self, expedition):
        self.ensure_one()
        
        return {
            'code': None,
            'delivery_code': None,
            'date': None,
            'hour': None,
            'observations': None,
            'state': None,
            'state_code': None,
            'exps_rels': None,
        }

    @api.one
    def generate_shipping_expedition(self):
        return True

    @api.multi
    def action_generate_shipping_expedition(self):
        for obj in self:
            if obj.shipping_expedition_id.id==0:
                obj.generate_shipping_expedition()
                
    @api.one    
    def action_error_create_shipping_expedition_message_slack(self, res):
        return                        