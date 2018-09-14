# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api
from openerp import exceptions
from openerp.tools.translate import _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def _create_extra_moves(self, picking):
        User = self.pool['res.users']
        can_create = (
            User.has_group(
                self.env.cr, self.env.user.id,
                'specific_stock.group_utb_no_quantity_check'
            ) or
            User.has_group(
                self.env.cr, self.env.user.id,
                'specific_stock.group_utb_can_increase_quantity'
            )
        )
        if not can_create:
            if picking.picking_type_id.code != 'incoming':
                raise exceptions.Warning(
                    _('Forbidden operation'),
                    _('You are not allowed to process the specified '
                      'quantities as they would create extra moves. '
                      'This can cause stock corruption. Someone maybe '
                      'already processed the picking, '
                      'or you increased the quantities beyond what was '
                      'originally scheduled.')
                )
        return super(StockPicking, self)._create_extra_moves(picking)
