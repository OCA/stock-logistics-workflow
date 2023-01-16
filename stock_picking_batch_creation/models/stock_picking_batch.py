# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingBatch(models.Model):

    _inherit = "stock.picking.batch"
    picking_device_id = fields.Many2one("stock.device.type", string="Device")
    batch_weight = fields.Float(
        string="Total weight",
        help="Indicates total weight of transfers included.",
    )
    batch_volume = fields.Float(
        string="Total volume",
        help="Indicates total volume of transfers included.",
    )
    batch_nbr_bins = fields.Integer(
        string="Number of compartments",
        help="Indicates the bins occupied by the pickings on the device.",
    )
    batch_nbr_lines = fields.Integer(
        string="Number of picking lines",
        help="Indicates the picking lines ready for preparation.",
    )

    def _init_batch_info(self, used_nbr_bins):
        """Store initial result of the batch computation"""
        self.ensure_one()
        pickings = self.picking_ids.with_prefetch()
        info = {
            "batch_weight": sum(
                [picking.total_weight_batch_picking for picking in pickings]
            ),
            "batch_volume": sum(
                [picking.total_volume_batch_picking for picking in pickings]
            ),
            "batch_nbr_bins": used_nbr_bins,
            "batch_nbr_lines": sum([picking.nbr_picking_lines for picking in pickings]),
        }
        self.write(info)

    def write(self, vals):
        res = super(StockPickingBatch, self).write(vals)
        for rec in self:
            if "user_id" in vals.keys():
                rec.picking_ids.write({"user_id": vals["user_id"]})
        return res
