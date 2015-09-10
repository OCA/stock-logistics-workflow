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

    package_preparation_id = fields.Many2one(
        'stock.picking.package.preparation', string='Stock Move',
        ondelete='cascade')
    name = fields.Text(string='Description', required=True)
    move_id = fields.Many2one('stock.move', string='Stock Move',
                              ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product')
    product_uom_qty = fields.Float(
        digits_compute=dp.get_precision('Product Unit of Measure'),
        help="If you change this quantity for a 'ready' picking, the system "
             "will not generate a back order, but will just deliver the new "
             "quantity")
    product_uom = fields.Many2one('product.uom')
    sequence = fields.Integer()
    note = fields.Text()

    @api.multi
    def write(self, values):
        super(StockPickingPackagePreparationLine, self).write(values)
        if 'product_uom_qty' in values and self.move_id:
            if self.move_id.product_uom_qty != values['product_uom_qty']:
                self.move_id.product_uom_qty = values['product_uom_qty']
                # perform a new reservation with the new quantity
                self.move_id.picking_id.do_unreserve()
                self.move_id.picking_id.action_assign()

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

    @api.multi
    def get_move_data(self):
        self.ensure_one()
        return {
            'name': self.name,
            'product_id': self.product_id.id,
            'product_uom_qty': self.product_uom_qty,
            'product_uom': self.product_uom.id,
            }


class StockPickingPackagePreparation(models.Model):

    _inherit = 'stock.picking.package.preparation'

    FIELDS_STATES = {'done': [('readonly', True)],
                     'in_pack': [('readonly', True)],
                     'cancel': [('readonly', True)]}

    picking_type_id = fields.Many2one(related='picking_ids.picking_type_id')
    line_ids = fields.One2many(
        'stock.picking.package.preparation.line',
        'package_preparation_id',
        string='Details',
        copy=False,
        states=FIELDS_STATES)

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
        return super(StockPickingPackagePreparation, self).write(values)

    @api.multi
    def action_put_in_pack(self):
        # ----- Create a stock move and stock picking related with
        #       StockPickingPackagePreparationLine if this one has
        #       a product in the values
        picking_model = self.env['stock.picking']
        move_model = self.env['stock.move']
        for package in self:
            picking_type = package.picking_type_id or \
                self.env.ref('stock.picking_type_out')
            moves = []
            for line in package.line_ids:
                # ----- If line has 'move_id' this means we don't need to
                #       recreate picking and move again
                if line.product_id and not line.move_id:
                    move_data = line.get_move_data()
                    move_data.update({
                        'partner_id': package.partner_id.id,
                        'location_id':
                            picking_type.default_location_src_id.id,
                        'location_dest_id':
                            picking_type.default_location_dest_id.id,
                        })
                    moves.append((line, move_data))
            if moves:
                picking_data = {
                    'move_type': 'direct',
                    'partner_id': package.partner_id.id,
                    'company_id': package.company_id.id,
                    'date': package.date,
                    'picking_type_id': picking_type.id,
                    }
                picking = picking_model.create(picking_data)
                for line, move_data in moves:
                    move_data.update({'picking_id': picking.id})
                    move = move_model.create(move_data)
                    line.move_id = move.id
                # ----- Set the picking as "To DO" and try to set it as
                #       assigned
                picking.action_confirm()
                # ----- Show an error if a picking is not confirmed
                if picking.state != 'confirmed':
                    raise exceptions.Warning(
                        _('Impossible to create confirmed picking. '
                          'Please Check products availability!'))
                picking.action_assign()
                # ----- Show an error if a picking is not assigned
                if picking.state != 'assigned':
                    raise exceptions.Warning(
                        _('Impossible to create confirmed picking. '
                          'Please Check products availability!'))
                # ----- Add the relation between the new picking
                #       and PackagePreparation
                package.picking_ids = [(4, picking.id)]
        return super(StockPickingPackagePreparation, self).action_put_in_pack()
