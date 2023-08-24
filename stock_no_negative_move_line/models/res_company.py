from odoo import models, fields


class Company(models.Model):
    _inherit = 'res.company'

    prevent_negative_quantity_on = fields.Selection(
        string="Prevent Negative Quantity On",
        selection=[
            ("validation", "Validation"),
            ("move_line", "Move Line"),
        ],
    )
