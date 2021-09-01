# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPickingWave(models.Model):

    _inherit = "stock.picking.wave"
    picking_device_id = fields.Many2one("stock.device.type", string="Device")
    move_ids = fields.One2many(
        "stock.move", string="Stock moves", compute="_compute_move_ids"
    )
    pack_operation_ids = fields.One2many(
        "stock.pack.operation",
        string="Stock pack operations",
        compute="_compute_move_ids",
        readonly=True,
        states={"draft": [("readonly", False)], "in_progress": [("readonly", False)]},
    )
    wave_weight = fields.Float(
        string="Total weight", help="Indicates total weight of transfers included.",
    )
    wave_volume = fields.Float(
        string="Total volume", help="Indicates total volume of transfers included.",
    )
    wave_nbr_bins = fields.Integer(
        string="Number of compartments",
        help="Indicates the bins occupied by the pickings on the device.",
    )
    wave_nbr_lines = fields.Integer(
        string="Number of picking lines",
        help="Indicates the picking lines ready for preparation.",
    )

    @api.depends(
        "picking_ids",
        "picking_ids.pack_operation_ids",
        "picking_ids.move_lines",
        "picking_ids.move_lines.state",
    )
    def _compute_move_ids(self):
        for batch in self:
            batch.move_ids = batch.picking_ids.mapped("move_lines")
            batch.pack_operation_ids = batch.picking_ids.mapped("pack_operation_ids")

    def _init_wave_info(self, used_nbr_bins):
        """Store initial result of the wave computation"""
        self.ensure_one()
        pickings = self.picking_ids.with_prefetch()
        info = {
            "wave_weight": sum(
                [picking.total_weight_batch_picking for picking in pickings]
            ),
            "wave_volume": sum(
                [picking.total_volume_batch_picking for picking in pickings]
            ),
            "wave_nbr_bins": used_nbr_bins,
            "wave_nbr_lines": sum([picking.nbr_picking_lines for picking in pickings]),
        }
        self.write(info)
