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

""" Template of product pulled flow object """

from openerp.osv.orm import Model

from openerp.addons.stock_orderpoint_creator.base_product_config_template import BaseProductConfigTemplate


class ProductPulledFlow(BaseProductConfigTemplate, Model):
    _name = 'product.pulled.flow.template'

    _inherit = 'product.pulled.flow'
    _table = 'product_pulled_flow_template'

    _clean_mode = 'unlink'

    def _get_ids_2_clean(self, cursor, uid, template_br, product_ids, context=None):
        """ hook to select model specific objects to clean
        return must return a list of id"""
        model_obj = self._get_model()
        ids_to_del = model_obj.search(cursor, uid,
                                      [('product_id', 'in', product_ids)])
        return ids_to_del
