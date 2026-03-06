from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    picking_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Picking Partner",
        related="picking_id.partner_id",
        store=True,
        index=True,
        readonly=True,
    )
