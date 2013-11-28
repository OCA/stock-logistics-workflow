# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#   Author: Leonardo Pistone <leonardo.pistone@camptocamp.com>                #
#   Copyright 2013 Camptocamp SA                                              #
#                                                                             #
#   This program is free software: you can redistribute it and/or modify      #
#   it under the terms of the GNU Affero General Public License as            #
#   published by the Free Software Foundation, either version 3 of the        #
#   License, or (at your option) any later version.                           #
#                                                                             #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU Affero General Public License for more details.                       #
#                                                                             #
#   You should have received a copy of the GNU Affero General Public License  #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

from osv import osv
from tools.translate import _


class stock_move(osv.osv):
    _inherit = 'stock.move'

    def open_lot(self, cr, uid, ids, context=None):
        """If there is a production lot, open it in a form

        If the production lot has custom attributes, these are shown in a
        dynamic view

        """

        if context is None:
            context = {}
        for move in self.browse(cr, uid, ids, context=context):
            if move.prodlot_id:
                ctx = {}
                domain = []

                if move.prodlot_id.attribute_set_id:
                    ctx = (
                        "{'open_lot_by_attribute_set': True, "
                        "'attribute_group_ids': %s}"
                        % [
                            group.id
                            for group in move.prodlot_id.attribute_set_id.attribute_group_ids
                        ]
                    )
                    domain = (
                        "[('attribute_set_id', '=', %s)]"
                        % move.prodlot_id.attribute_set_id.id
                    )

                return {
                    'context':ctx,
                    'domain': domain,
                    'res_id': move.prodlot_id.id,
                    'name': _('Production Lots'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'stock.production.lot',
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                }
