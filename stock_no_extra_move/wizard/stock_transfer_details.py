# -*- coding: utf-8 -*-
# Copyright 2018 Julien Coux (Camptocamp SA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, exceptions, models, _


class StockTransferDetailsItems(models.TransientModel):
    _inherit = 'stock.transfer_details_items'

    @api.one
    @api.constrains('quantity', 'orig_quantity')
    def _check_quantities(self):
        User = self.pool['res.users']
        if self.quantity < 0:
            raise exceptions.Warning(_('Negative quantity'))

        else:
            if not User.has_group(
                    self.env.cr, self.env.user.id,
                    'stock_no_extra_move.group_can_increase_quantity'
            ):
                allowed_quantity = self.orig_quantity
                if User.has_group(
                        self.env.cr, self.env.user.id,
                        'stock_no_extra_move.group_can_increase_quantity'
                ):
                    percent_increase_quantity_allowed = self.env[
                        'stock.config.settings'
                    ].get_default_percent_increase_quantity_allowed()[
                        'percent_increase_quantity_allowed'
                    ]
                    allowed_quantity *= 1 + (
                        percent_increase_quantity_allowed / 100.
                    )
                if self.quantity > allowed_quantity:
                    raise exceptions.Warning(_(
                        'You cannot increase quantity more than %.2f'
                    ) % allowed_quantity)

        return True
