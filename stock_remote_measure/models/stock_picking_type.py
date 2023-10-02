# Copyright 2023 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    remote_scale_id = fields.Many2one(
        comodel_name="remote.measure.device",
        help="Scale used by default in this operations",
    )
