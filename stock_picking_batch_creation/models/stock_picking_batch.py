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

    def write(self, vals):
        res = super(StockPickingBatch, self).write(vals)
        for rec in self:
            if "user_id" in vals.keys() and not vals["user_id"]:
                # We want to  unassign the batch from the operator
                # and the pickings in the batch too. We must force the method
                # write on the picking since the base class propagate the
                # user_id only if it's set (not if it's unset)
                rec.picking_ids.write({"user_id": vals["user_id"]})
        return res
