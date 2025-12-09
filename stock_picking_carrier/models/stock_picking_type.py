# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    carrier_auto_assign_picking = fields.Boolean(
        string="Carrier auto assign",
        compute="_compute_carrier_auto_assign_picking",
        readonly=False,
        store=True,
        help="Assign the carrier in the picking when the partner or the "
        "main partner has the shipping method assigned.",
    )

    @api.depends("company_id.carrier_auto_assign_picking")
    def _compute_carrier_auto_assign_picking(self):
        for picking_type in self:
            picking_type.carrier_auto_assign_picking = (
                picking_type.company_id.carrier_auto_assign_picking
            )
