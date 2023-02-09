# Copyright 2023 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    remote_scale_id = fields.Many2one(
        comodel_name="remote.measure.device",
        default=lambda self: self.env["stock.picking.type"]
        .browse(self._context.get("default_picking_type_id"))
        .remote_scale_id,
        states={"done": [("readonly", True)]},
    )
