# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    @api.model
    def _get_selection_split_method_landed_cost_line(self):
        model = self.env["stock.landed.cost.lines"]
        return model.fields_get(allfields=["split_method"])["split_method"]["selection"]

    create_landed_cost_line = fields.Boolean(
        string="Allow create landed cost lines", default=True
    )
    split_method_landed_cost_line = fields.Selection(
        selection="_get_selection_split_method_landed_cost_line",
        string="Split method",
        default="by_quantity",
        help="Split method used in landed cost lines",
    )
