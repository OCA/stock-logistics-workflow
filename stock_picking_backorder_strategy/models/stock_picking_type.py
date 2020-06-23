# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, _, api


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    backorder_strategy = fields.Selection(
        [('manual', _('Manual')), ('create', _('Create')),
         ('no_create', _('No create')),
         ('cancel', _('Cancel'))],
        default='manual',
        help="Define what to do with backorder",
        required=True
    )

    disable_move_lines_split = fields.Boolean(_('Disable Move Split'),
        help=_("Checking this option will prevent stock moves from being \
        splited in cases where quantity done is smaller than expected")
        #This avoids the creation of stock moves that we create only to cancel afterwords
    )

    disable_backorder_only_on_picking_validation = fields.Boolean(_('Disable Backorder only on picking validation'),
        help=_("Checking this option with avoid backorder other creating if it is being called inside stock.picking action_done method")
    )

    @api.onchange('backorder_strategy')
    def _on_backorder_strategy_change(self):
        for record in self:
            record.disable_move_lines_split = False
            record.disable_backorder_only_on_picking_validation = False


