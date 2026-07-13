# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    manufacturing_picking_id = fields.Many2one(
        "stock.picking", string="Manufacturing Picking"
    )
