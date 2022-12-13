# Copyright 2015 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockGrnType(models.Model):
    """GRN Type"""

    _name = "stock.grn.type"
    _description = "Type of goods received note"

    name = fields.Char(string="Type", required=True)

    _sql_constraints = [
        ("name_uniq", "unique (name)", "This GRN type name already exists !")
    ]
