# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockDeviceType(models.Model):

    _name = "stock.device.type"
    _description = "Stock Device Type"

    name = fields.Char()
    min_volume = fields.Float(
        string="Minimum total net volume for electing this device (in m3)"
    )
    max_volume = fields.Float(
        string="Maximum total net volume for electing this device (in m3)"
    )
    max_weight = fields.Float(
        string="Maximum total net weight for electing this device (in kg)"
    )
    nbr_bins = fields.Integer(string="Number of compartments")

    volume_per_bin = fields.Float(
        string="Max volume per bin", compute="_compute_volume_per_bin"
    )

    sequence = fields.Integer(string="Priority")

    @api.depends("max_volume", "nbr_bins")
    def _compute_volume_per_bin(self):
        for rec in self:
            vol = 0
            if rec.max_volume and rec.nbr_bins:
                vol = rec.max_volume / rec.nbr_bins
            rec.volume_per_bin = vol
