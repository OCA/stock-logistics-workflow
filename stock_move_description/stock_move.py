# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-15 Agile Business Group sagl
#    (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp.osv import orm, fields


class StockMove(orm.Model):
    _inherit = "stock.move"

    _columns = {
        'name': fields.text('Description'),
    }

    def onchange_product_id(
            self, cr, uid, ids, prod_id=False, loc_id=False,
            loc_dest_id=False, partner_id=False, context=None
    ):
        context = dict(context or {})
        res = super(StockMove, self).onchange_product_id(
            cr, uid, ids, prod_id=prod_id, loc_id=loc_id,
            loc_dest_id=loc_dest_id, partner_id=partner_id
        )
        if prod_id:
            user = self.pool.get('res.users').browse(
                cr, uid, uid, context=context)
            lang = user and user.lang or False
            if partner_id:
                addr_rec = self.pool.get('res.partner').browse(
                    cr, uid, partner_id, context=context)
                if addr_rec:
                    lang = addr_rec and addr_rec.lang or False
            context['lang'] = lang
            user_groups = [g.id for g in user.groups_id]
            group_ref = self.pool.get('ir.model.data').get_object_reference(
                cr, uid, 'stock_move_description',
                'group_use_product_description_per_stock_move'
            )
            if group_ref and group_ref[1] in user_groups:
                product_obj = self.pool.get('product.product')
                product = product_obj.browse(
                    cr, uid, prod_id, context=context)
                if product.description:
                    if 'value' not in res:
                        res['value'] = {}
                    res['value']['name'] = product.description
        return res
