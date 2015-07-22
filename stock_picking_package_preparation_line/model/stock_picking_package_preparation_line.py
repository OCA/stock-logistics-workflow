# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Francesco Apruzzese
#    Copyright 2015 Apulia Software srl
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

from openerp import models, fields, api, exceptions, _
import openerp.addons.decimal_precision as dp


class StockPickingPackagePreparationLine(models.Model):

    _name = 'stock.picking.package.preparation.line'
    _description = 'Package Preparation Line'
    _inherit = ['mail.thread']

    package_preparation_id = fields.Many2one('stock.move', string='Sock Move')
    name = fields.Text(string='Description', required=True)
    move_id = fields.Many2one('stock.move', string='Sock Move')
    product_id = fields.Many2one('product.product', string='Product')
    product_uom_qty = fields.Float(
        digits_compute=dp.get_precision('Product Unit of Measure'))
    product_uom = fields.Many2one('product.uom')
    note = fields.Text()

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            name = self.product_id.name_get()
            if name:
                self.name = name[0][1]


class StockPickingPackagePreparation(models.Model):

    _inherit = 'stock.picking.package.preparation'

    line_ids = fields.One2many('stock.picking.package.preparation.line',
                               'package_preparation_id')
