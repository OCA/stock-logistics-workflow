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

    user_id = fields.Many2one(
        "res.users",
        string="Responsible",
        readonly=True,
        default=lambda p: p.batch_id.user_id,
        copy=False,
    )
    total_weight_batch_picking = fields.Float(
        string="Total Weight for transfers",
        help="Indicates total weight of transfers included.",
    )
    total_volume_batch_picking = fields.Float(
        string="Volume",
        help="Indicates total volume of transfers included.",
    )
    nbr_bins_batch_picking = fields.Integer(
        string="Number of compartments",
        help="Indicates the bins occupied by the picking on the device.",
    )
    nbr_picking_lines = fields.Integer(
        string="Number of lines",
        help="Indicates the picking lines ready for preparation.",
        compute="_compute_nbr_picking_lines",
    )

    def _refresh_dimension_fields(self):
        self._init_dimension_fields(force=True)

    def _refresh_nbr_bins_on_device_field(self, device):
        self._init_nbr_bins_on_device_field(device, force=True)

    def _init_nbr_bins_on_device_field(self, device, force=False):
        """Initialize nbr_bin batch picking on demand"""
        for record in self:
            to_write = {}
            if not record.nbr_bins_batch_picking or force:
                nbr_bins = self._get_nbr_bin_batch_for_device(device)
                if nbr_bins != record.nbr_bins_batch_picking:
                    to_write["nbr_bins_batch_picking"] = nbr_bins
            if to_write:
                record.write(to_write)

    def _init_dimension_fields(self, force=False):
        """Initialize dimension fields on demand since the computation of these
        fields is very expensive"""
        for record in self:
            to_write = {}
            if not record.total_weight_batch_picking or force:
                total_weight = self._get_total_weight_batch_picking()
                if total_weight != record.total_weight_batch_picking:
                    to_write["total_weight_batch_picking"] = total_weight
            if not record.total_volume_batch_picking or force:
                total_volume = self._get_total_volume_batch_picking()
                if total_volume != record.total_volume_batch_picking:
                    to_write["total_volume_batch_picking"] = total_volume
            if to_write:
                record.write(to_write)

    def _get_total_weight_batch_picking(self):
        self.ensure_one()
        weight = 0.0
        for line in self.move_ids.filtered(lambda m: m.reserved_availability):
            weight += line.product_id.get_total_weight_from_packaging(
                line.reserved_availability
            )
        return weight

    def _get_total_volume_batch_picking(self):
        self.ensure_one()
        volume = 0.0
        for line in self.move_ids.filtered(lambda m: m.reserved_availability):
            product = line.product_id.with_context(_packaging_filter=lambda p: p.volume)
            packagings_with_volume = product.product_qty_by_packaging(
                line.reserved_availability
            )
            for packaging_info in packagings_with_volume:
                if packaging_info.get("is_unit"):
                    pack_volume = product.volume
                else:
                    packaging = self.env["product.packaging"].browse(
                        packaging_info["id"]
                    )
                    pack_volume = packaging.volume

                volume += pack_volume * packaging_info["qty"]
        return volume

    def _get_nbr_bin_batch_for_device(self, device):
        self.ensure_one()
        nbr_bins = 0
        if self.total_volume_batch_picking:
            nbr_bins = math.ceil(
                self.total_volume_batch_picking / device.volume_per_bin
            )
        else:
            nbr_bins = 1
        return nbr_bins

    @api.depends("move_line_ids")
    def _compute_nbr_picking_lines(self):
        for rec in self:
            rec.nbr_picking_lines = len(rec.move_line_ids)
