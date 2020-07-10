# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models, fields

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    shipping_expedition_note = fields.Text(
        string='Expedition Note',
    )

    shipping_expedition_count = fields.Integer(
        compute='_compute_shipping_expedition_count',
        string="Expeditions",
    )

    def _compute_shipping_expedition_count(self):
        for item in self:
            item.shipping_expedition_count = len(self.env['shipping.expedition'].search([('order_id', '=', item.id)]))

    @api.multi
    def action_confirm(self):
        return_data = super(SaleOrder, self).action_confirm()
        # operations
        for item in self:
            if item.state == 'sale':
                for picking_id in item.picking_ids:
                    picking_id.shipping_expedition_note = item.shipping_expedition_note
        # return
        return return_data