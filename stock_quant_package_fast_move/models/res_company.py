# Copyright (C) 2023 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    package_move_picking_type_id = fields.Many2one(
        "stock.picking.type",
        string="Package Move Operation",
        domain="[('show_entire_packs', '=', True)]",
    )
