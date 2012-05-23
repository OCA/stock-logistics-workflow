# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher (Camptocamp)
#    Copyright 2012 Camptocamp SA
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

""" Overload of orderpoint creator Wizard to add location flow configurations 
for selected products. Those configs are generated using templates """

from osv import osv, fields

_template_register = ['push_flow_template_id', 'pull_flow_template_id']

class ProductConfigCreator(osv.osv_memory):
    _inherit = 'stock.warehouse.orderpoint.creator'
    _description = 'Orderpoint Creator'

    _columns = {
            'push_flow_template_id': fields.many2one(
                'stock.location.path.template',
                "Pushed Flows"),
            'pull_flow_template_id': fields.many2one(
                'product.pulled.flow.template',
                "Pulled Flows")
    }

    def _get_template_register(self):
        """return a list of the field names which defines a template
        This is a hook to allow expending the list of template"""
        template_reg = []
        parent_reg = super(ProductConfigCreator, self)._get_template_register()
        template_reg.extend(parent_reg)
        template_reg.extend(_template_register)
        return template_reg

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
