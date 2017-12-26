# © 2014-2016 Camptocamp SA (Guewen Baconnier)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import logging
from odoo import api, models
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def check_assign_all(self):
        """ Try to assign confirmed pickings """
        pickings = self
        if not pickings:
            domain = [('picking_type_code', '=', 'outgoing'),
                      ('state', '=', 'confirmed')]
            pickings = self.search(domain, order='min_date')

        for picking in pickings:
            try:
                picking.action_assign()
            except Exception:
                # ignore the error, the picking will just stay as confirmed
                name = picking.name
                _logger.exception(_('error in action_assign for picking %s')
                                  % name, exc_info=True)
        return True
