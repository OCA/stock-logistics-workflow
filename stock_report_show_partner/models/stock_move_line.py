# Copyright 2021 Daniel Domínguez - https://xtendoo.es
# Copyright 2021 Manuel Calero - https://xtendoo.es
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        related="picking_id.partner_id",
        string="Partner",
        readonly=True,
    )
