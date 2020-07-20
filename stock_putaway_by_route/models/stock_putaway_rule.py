# Copyright 2020 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockPutawayRule(models.Model):
    _inherit = "stock.putaway.rule"

    route_id = fields.Many2one(
        comodel_name="stock.location.route",
        string="Route",
        check_company=True,
        ondelete="cascade",
    )
