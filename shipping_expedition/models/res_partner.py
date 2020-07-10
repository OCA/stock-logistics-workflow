# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    shipping_expedition_count = fields.Integer(
        compute='_compute_shipping_expedition_count',
        string="Expeditions",
    )

    def _compute_shipping_expedition_count(self):
        for item in self:
            item.shipping_expedition_count = len(self.env['shipping.expedition'].search([('partner_id', 'child_of', item.ids)]))