# Copyright 2022 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResCompany(models.Model):

    _inherit = "res.company"

    stock_picking_assign_operator_at_start = fields.Boolean(
        "Assign responsible on stock picking start", default=False
    )
