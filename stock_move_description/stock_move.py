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

from odoo import fields, models, api


class StockMove(models.Model):
    _inherit = "stock.move"
    name = fields.Text(string="Description", required=False, )

    @api.onchange('product_id')
    def onchange_product_id(
            self, prod_id=False, loc_id=False,
            loc_dest_id=False, partner_id=False
    ):

        res = super(StockMove, self).onchange_product_id(
             prod_id=prod_id, loc_id=loc_id,
            loc_dest_id=loc_dest_id, partner_id=partner_id
        )
        if prod_id:
            user = self.env.user['res.users']

            lang = user and user.lang or False
            if partner_id:
                addr_rec = self.env['res.partner'].browse(partner_id)
                if addr_rec:
                    lang = addr_rec and addr_rec.lang or False
            self.env.lang = lang
            user_groups = [g.id for g in user.groups_id]
            group_ref = self.env['ir.model.data'].get_object_reference(
                 'stock_move_description',
                'group_use_product_description_per_stock_move'
            )
            if group_ref and group_ref[1] in user_groups:
                product_obj = self.env['product.product']
                product = product_obj.browse(  prod_id)
                if product.description:
                    if 'value' not in res:
                        res['value'] = {}
                    res['value']['name'] = product.description
        return res
