# -*- coding: utf-8 -*-
##############################################################################
#
#    Product serial module for Odoo
#    Copyright (C) 2008 Raphaël Valyi
#    Copyright (C) 2013-2015 Akretion (http://www.akretion.com/)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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

from openerp import fields, models


# TODO : migration script from PP to PT
class ProductTemplate(models.Model):
    _inherit = "product.template"

    lot_split_type = fields.Selection([
        ('none', 'None'),
        ('single', 'Single'),
        # ('lu', 'Logistical Unit')  # TODO : restore if someone needs it
        ], string='Lot split type', required=True, default='none',
        help="You should select 'Single' if you have one serial number per "
        "item. In this case, the Transfer pop-up on the picking will "
        "display one line per unit for this product. "
        "The default value is 'None': for those product, the native "
        "process is not modified.")
