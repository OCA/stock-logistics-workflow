# -*- coding: utf-8 -*-
# © 2014-2016 Camptocamp SA (Guewen Baconnier)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import logging
from openerp import api, models

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    @api.multi
    def check_assign_all(self):
        """ Try to assign confirmed pickings """
        if self is None:
            domain = [('type', '=', 'out'),
                      ('state', '=', 'confirmed')]
            self = self.search(domain, order='min_date')

        for picking in self:
            try:
                picking.action_assign()
            except Exception:
                # ignore the error, the picking will just stay as confirmed
                name = picking.name
                _logger.info('error in action_assign for picking %s',
                             name, exc_info=True)
        return True
