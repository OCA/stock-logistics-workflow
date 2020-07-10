# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models, fields

import logging
_logger = logging.getLogger(__name__)

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    shipping_expedition_count = fields.Integer(
        compute='_compute_shipping_expedition_count',
        string="Expeditions",
    )

    def _compute_shipping_expedition_count(self):
        for item in self:
            item.shipping_expedition_count = len(self.env['shipping.expedition'].search([('order_id', 'in', item.order_ids.ids)]))