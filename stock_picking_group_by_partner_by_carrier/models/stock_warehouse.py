# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    group_shippings = fields.Boolean(
        related="out_type_id.group_pickings",
        readonly=False,
    )
    group_shippings_one = fields.Boolean(
        related="out_type_id.group_pickings_one",
        readonly=False,
    )
