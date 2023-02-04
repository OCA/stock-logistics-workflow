# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import math

from odoo import api, fields, models


class StockPicking(models.Model):

    _inherit = "stock.picking"
    picking_device_id = fields.Many2one(
        "stock.device.type",
        string="Device for the picking",
        related="batch_id.picking_device_id",
        readonly=True,
    )
    nbr_picking_lines = fields.Integer(
        string="Number of lines",
        help="Indicates the picking lines ready for preparation.",
        compute="_compute_nbr_picking_lines",
        store=True,
    )

    def _get_nbr_bins_for_device(self, device):
        self.ensure_one()
        if not device:
            return 0
        if not self.volume:
            return 1
        return math.ceil(self.volume / device.volume_per_bin)

    @api.depends("move_line_ids")
    def _compute_nbr_picking_lines(self):
        for rec in self:
            rec.nbr_picking_lines = len(rec.move_line_ids)
