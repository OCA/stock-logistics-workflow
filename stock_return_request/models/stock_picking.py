# Copyright 2019 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    stock_return_request_id = fields.Many2one(
        comodel_name='stock.return.request',
    )

    def _create_backorder(self, backorder_moves=None):
        """When we make a backorder of a picking in a return request, we
           want to have it linked to the return request itself """
        if backorder_moves is None:
            backorder_moves = []
        backorders = super()._create_backorder(backorder_moves)
        rbo = backorders.filtered('backorder_id.stock_return_request_id')
        for backorder in rbo:
            backorder.stock_return_request_id = (
                backorder.backorder_id.stock_return_request_id)
        return backorders
