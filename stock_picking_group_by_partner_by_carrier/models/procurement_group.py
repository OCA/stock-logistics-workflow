from odoo import fields, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    carrier_id = fields.Many2one("delivery.carrier", string="Delivery Method")
