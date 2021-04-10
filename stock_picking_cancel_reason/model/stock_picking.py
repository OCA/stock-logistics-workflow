# Copyright 2021 Ecosoft Co., Ltd (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    cancel_reason_id = fields.Many2one(
        comodel_name="stock.picking.cancel.reason",
        string="Reason for cancellation",
        readonly=True,
        ondelete="restrict",
    )
    cancel_description = fields.Text(
        string="Description for cancellation", readonly=True
    )


class StockPickingCancelReason(models.Model):
    _name = "stock.picking.cancel.reason"
    _description = "Stock Picking Cancel Reason"

    name = fields.Char(string="Reason", required=True, translate=True)
    active = fields.Boolean(default=True)
