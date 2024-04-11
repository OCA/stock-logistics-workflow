# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)


from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    assign_owner = fields.Boolean(
        "Assign owner automatically",
        help="If checked, the owner of the picking will be the partner of the picking.",
    )
