from odoo import fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    lot_info_usage = fields.Selection(
        [("no", "No"), ("optional", "Optional"), ("required", "Required")],
        default="no",
        string="Lot Information Usage",
    )
