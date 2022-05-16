# Copyright 2015-17 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    backorder_ids = fields.One2many(
        comodel_name="stock.picking",
        inverse_name="backorder_id",
        copy=False,
        string="Backorders",
        readonly=True,
    )
