# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'
    
    carrier_type = fields.Selection(
        selection=[
            ('none', 'None'),
            ('cbl', 'Cbl'),
            ('nacex', 'Nacex'),
            ('tsb', 'Tsb'),
            ('txt', 'Txt'),
        ],
        string='Type',
        default='none'
    )    