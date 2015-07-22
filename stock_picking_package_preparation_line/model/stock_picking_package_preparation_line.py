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

    package_preparation_id = fields.Many2one(
        'stock.picking.package.preparation', string='Stock Move',
        ondelete='cascade')
    name = fields.Text(string='Description', required=True)
    move_id = fields.Many2one('stock.move', string='Stock Move')
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
            self.product_uom = self.product_id.uom_id.id

    def _prepare_lines_from_pickings(self, picking_ids):
        lines = []
        if not picking_ids:
            return lines
        picking_model = self.env['stock.picking']
        for picking in picking_model.browse(picking_ids):
            for move_line in picking.move_lines:
                # ----- search if the move is related with a
                #       PackagePreparationLine, yet. If not, create a new line
                if not self.search([('move_id', '=', move_line.id)],
                                   count=True):
                    lines.append({
                        'move_id': move_line.id,
                        'name': move_line.product_id.name_get()[0][1],
                        'product_id': move_line.product_id.id,
                        'product_uom_qty': move_line.product_uom_qty,
                        'product_uom': move_line.product_uom.id,
                        })
        return lines


class StockPickingPackagePreparation(models.Model):

    _inherit = 'stock.picking.package.preparation'

    line_ids = fields.One2many('stock.picking.package.preparation.line',
                               'package_preparation_id')

    @api.model
    def create(self, values):
        # ----- Create a PackagePreparationLine for every stock move
        #       in the pickings added to PackagePreparation
        if values.get('picking_ids', False):
            package_preparation_lines = self.env[
                'stock.picking.package.preparation.line'
                ]._prepare_lines_from_pickings(values['picking_ids'][0][2])
            if package_preparation_lines:
                values.update({
                    'line_ids': [(0, 0, v) for v in package_preparation_lines]
                })
        return super(StockPickingPackagePreparation, self).create(values)

    @api.multi
    def write(self, values):
        if values.get('picking_ids', False):
            package_preparation_lines = self.env[
                'stock.picking.package.preparation.line'
                ]._prepare_lines_from_pickings(values['picking_ids'][0][2])
            if package_preparation_lines:
                values.update({
                    'line_ids': [(0, 0, v) for v in package_preparation_lines]
                })
        return super(StockPickingPackagePreparation, self).write(values)
