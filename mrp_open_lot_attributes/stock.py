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
from lxml import etree


class stock_move(osv.osv):
    _inherit = 'stock.move'

    def open_lot(self, cr, uid, ids, context=None):
        """Open Production Lot in a form, with attributes if any

        If the production lot has custom attributes, these are shown in a
        dynamic view

        """

        if context is None:
            context = {}
        for move in self.browse(cr, uid, ids, context=context):
            # existing lot
            if move.prodlot_id:
                ctx = {'add_save_close': True}
                domain = []

                if move.prodlot_id.attribute_set_id:
                    ctx['open_lot_by_attribute_set'] = True,
                    ctx['attribute_group_ids'] = [
                        group.id
                        for group in
                        move.prodlot_id.attribute_set_id.attribute_group_ids
                    ]

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

            # new lot
            else:
                ctx = {
                    'add_save_close': True,
                    'default_product_id': move.product_id.id,
                }

                return {
                    'context': ctx,
                    'name': _('Production Lots'),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'stock.production.lot',
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                }


class stock_production_lot(osv.osv):
    _inherit = 'stock.production.lot'

    def save_lot(self, cr, uid, ids, context=None):
        """If the lot is new, assign it to the original move"""

        assert len(ids) == 1
        if context['active_model'] == 'stock.move':
            move_pool = self.pool.get('stock.move')
            move = move_pool.browse(
                cr, uid, context['active_id'], context=context
            )
            if not move.prodlot_id:
                move_pool.write(cr, uid, [move.id], {
                    'prodlot_id': ids[0],
                })
        return {'type': 'ir.actions.act_window_close'}

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        """Dinamically adds Save and close, Cancel buttons to the form view

        """

        if context is None:
            context = {}

        result = super(stock_production_lot, self).fields_view_get(
            cr, uid, view_id, view_type, context, toolbar=toolbar,
            submenu=submenu
        )
        if view_type == 'form' and context.get('add_save_close'):
            eview = etree.fromstring(result['arch'])
            etree.SubElement(
                eview,
                'button',
                icon="gtk-cancel",
                special="cancel",
                string=_('Cancel'),
                colspan="2",
            )
            etree.SubElement(
                eview,
                'button',
                icon="gtk-ok",
                name="save_lot",
                string=_('Save and Close'),
                type="object",
                colspan="2",
            )
            result['arch'] = etree.tostring(eview, pretty_print=True)
        return result
