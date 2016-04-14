# -*- coding: utf-8 -*-
# © 2016 Lorenzo Battistini - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def action_back_to_draft(self):
        res = super(StockMove, self).action_back_to_draft()
        draft_pickings = self.mapped('picking_id')
        sales = draft_pickings.mapped('sale_id')
        sales.signal_workflow('ship_corrected')
        return res
