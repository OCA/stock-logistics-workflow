from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    prevent_negative_quantity_on = fields.Selection(
        string="Prevent Negative Quantity On",
        selection=[
            ("validation", "Validation"),
            ("move_line", "Move Line"),
        ],
        related='company_id.prevent_negative_quantity_on',
        readonly = False,
        help='Select when the user should be blocked if a move will result a negative quantity.'
    )
