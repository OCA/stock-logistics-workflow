# Copyright 2023 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    put_in_pack_restriction = fields.Selection(
        related="picking_type_id.put_in_pack_restriction"
    )
