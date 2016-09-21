# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging

from openerp import api
from openerp.osv import orm
from openerp.models import Model

_logger = logging.getLogger(__name__)


class StockPicking(Model):
    _inherit = 'stock.picking'

    @api.model
    def check_assign_all(self):
        """ Try to assign confirmed pickings """
        type_obj = self.env['stock.picking.type']
        out_type_ids = type_obj.search([('code', '=', 'outgoing')]).ids
        domain = [('picking_type_id', 'in', out_type_ids),
                  ('state', '=', 'confirmed')]
        records = self.search(domain, order='min_date')

        for record in records:
            try:
                record.action_assign()
            except orm.except_orm:
                # ignore the error, the picking will just stay as confirmed
                _logger.info('error in action_assign for picking %s',
                             record.name, exc_info=True)
