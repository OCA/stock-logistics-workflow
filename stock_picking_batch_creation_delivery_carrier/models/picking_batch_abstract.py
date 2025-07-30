# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class MakePickingBatchAbstract(models.AbstractModel):
    _inherit = "make.picking.batch.abstract"

    delivery_carrier_id = fields.Many2one(
        comodel_name="delivery.carrier",
        help="Fill in this if you want to filter the "
        "selected pickings with a delivery carrier",
    )
