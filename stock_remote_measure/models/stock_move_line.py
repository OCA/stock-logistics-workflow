# Copyright 2023 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    remote_scale_id = fields.Many2one(
        comodel_name="remote.measure.device",
        compute="_compute_remote_scale_id",
        readonly=False,
        store=True,
    )

    @api.depends("picking_id", "picking_id.remote_scale_id", "product_uom_id")
    def _compute_remote_scale_id(self):
        """We don't want to measure if the scale uom is not in the same category than
        the line"""
        for sml in self:
            scale = (
                sml.product_uom_id.category_id
                == sml.picking_id.remote_scale_id.uom_id.category_id
                and sml.picking_id.remote_scale_id
            )
            if not scale and self.env.context.get("force_user_measure_device"):
                scale = (
                    sml.product_uom_id.category_id
                    == self.env.user.remote_measure_device_id.uom_id.category_id
                    and self.env.user.remote_measure_device_id
                )
            if not scale:
                continue
            sml.remote_scale_id = scale
