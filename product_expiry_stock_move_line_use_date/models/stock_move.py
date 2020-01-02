# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models


class StockMove(models.Model):

    _inherit = "stock.move"

    show_lots_use_date_text = fields.Boolean(
        compute='_compute_show_lots_use_date_text'
    )

    @api.depends(
        'picking_id', 'picking_id.show_lots_text', 'product_id',
        'product_id.display_use_date_at_lot_creation'
    )
    def _compute_show_lots_use_date_text(self):
        for move in self:
            move.show_lots_use_date_text = (
                move.picking_id.show_lots_text and
                move.product_id.display_use_date_at_lot_creation
            )

    def action_show_details(self):
        res = super().action_show_details()
        context = res.get('context').copy()
        context['show_lots_date_use'] = (
            context.get('show_lots_text') and
            self.product_id.display_use_date_at_lot_creation
        )
        res['context'] = context
        return res


class StockMoveLine(models.Model):

    _inherit = "stock.move.line"

    show_lots_use_date_text = fields.Boolean(
        related='move_id.show_lots_use_date_text',
    )
    lot_use_date_name = fields.Datetime(string='Best before Date')

    def _action_done(self):
        self = self.with_context(copy_date_name_to_lot_mls=self.ids)
        return super()._action_done()
