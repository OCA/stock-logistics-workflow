from odoo import fields, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    sale_ids = fields.Many2many(comodel_name="sale.order", copy=True)
    picking_ids = fields.One2many(
        comodel_name="stock.picking",
        inverse_name="group_id",
        readonly=True,
    )
