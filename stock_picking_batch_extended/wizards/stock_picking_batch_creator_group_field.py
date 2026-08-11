# Copyright 2012-2016 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockBatchPickingCreatorGroupField(models.TransientModel):
    """Make mass batch pickings from grouped fields"""

    _name = "stock.picking.batch.creator.group.field"
    _description = "Batch Picking Creator Group Field"
    _order = "sequence, id"

    picking_to_batch_id = fields.Many2one(
        comodel_name="stock.picking.to.batch",
        ondelete="cascade",
        required=True,
    )
    sequence = fields.Integer(help="Group by picking field", default=0)
    field_id = fields.Many2one(
        comodel_name="ir.model.fields",
        string="Field to group",
        domain=[("model", "=", "stock.picking"), ("store", "=", True)],
        required=True,
    )
