# -*- coding: utf-8 -*-
#    Author: Francesco Apruzzese
#    Copyright 2015 Apulia Software srl
#    Copyright 2015 Lorenzo Battistini - Agile Business Group
#    Copyright 2016 Alessio Gerace - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError


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

    @api.multi
    def _update_line_ids(self):
        # Update package lines according to pickings.
        # Lines with move_id will be updated
        # Lines without move_id not be touched
        line_model = self.env['stock.picking.package.preparation.line']
        for pack in self:
            for line in pack.line_ids:
                if line.move_id:
                    line.unlink()
            package_preparation_lines = (
                line_model._prepare_lines_from_pickings(
                    [p.id for p in pack.picking_ids]))
            if package_preparation_lines:
                for line_vals in package_preparation_lines:
                    line_vals['package_preparation_id'] = pack.id
                    line_model.create(line_vals)

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, values):
        values = self._update_line_vals(values)
        pack = super(StockPickingPackagePreparation, self).create(values)
        return pack

    @api.model
    def _update_line_vals(self, values):
        """
        Create a PackagePreparationLine for every stock move
        in the pickings added to PackagePreparation
        """
        if values.get('picking_ids', False):
            picking_ids = []
            for pick_tuple in values['picking_ids']:
                if pick_tuple[0] == 6:
                    picking_ids.extend(pick_tuple[2])
                elif pick_tuple[0] == 4:
                    picking_ids.append(pick_tuple[1])
            package_preparation_lines = self.env[
                'stock.picking.package.preparation.line'
                ]._prepare_lines_from_pickings(picking_ids)
            if package_preparation_lines:
                origin_lines = []
                if 'line_ids' in values:
                    origin_lines = values.get('line_ids', [])
                origin_lines += [
                    (0, 0, v) for v in package_preparation_lines]
                values.update({
                    'line_ids': origin_lines
                })
        return values

    @api.multi
    def write(self, values):
        """
        Delete package preparation line if the relative picking is
        delete from package preparation
        """
        if values.get('picking_ids', False):
            package_preparation_line_model = self.env[
                'stock.picking.package.preparation.line']
            # Collect new pickings to read the change
            changed_picking_ids = []
            for picking_ids in values['picking_ids']:
                if picking_ids[0] == 6:
                    changed_picking_ids.extend(picking_ids[2])
            for pack in self:
                # Collect deleted pickings
                # to delete package preparation lines
                move_ids = [m.id
                            for p in pack.picking_ids
                            if p.id not in changed_picking_ids
                            for m in p.move_lines]
                if move_ids:
                    package_lines = package_preparation_line_model.search(
                        [('move_id', 'in', move_ids),
                         ('package_preparation_id', '=', pack.id)])
                    package_lines.unlink()
        values = self._update_line_vals(values)
        res = super(StockPickingPackagePreparation, self).write(values)
        return res

    @api.multi
    def action_put_in_pack(self):
        # Create a stock move and stock picking related with
        # StockPickingPackagePreparationLine if this one has
        # a product in the values
        picking_model = self.env['stock.picking']
        move_model = self.env['stock.move']
        default_picking_type = self.env.user.company_id.\
            default_picking_type_for_package_preparation_id or \
            self.env.ref('stock.picking_type_out')
        pack_model = self.env['stock.pack.operation']
        operation_lot = self.env['stock.pack.operation.lot']
        for package in self:
            picking_type = package.picking_type_id or default_picking_type
            moves = []
            for line in package.line_ids:
                # If line has 'move_id' this means we don't need to
                # recreate picking and move again
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
                if not (
                    picking_type.default_location_src_id and
                    picking_type.default_location_dest_id
                ):
                    msg = _(
                        'Cannot find a location for %s ' %
                        picking_type.name
                    )
                    raise UserError(msg)
                picking_data = {
                    'move_type': 'direct',
                    'partner_id': package.partner_id.id,
                    'company_id': package.company_id.id,
                    'date': package.date,
                    'picking_type_id': picking_type.id,
                    'location_id':
                        picking_type.default_location_src_id.id,
                    'location_dest_id':
                        picking_type.default_location_dest_id.id,
                    }
                picking = picking_model.create(picking_data)
                for line, move_data in moves:
                    move_data.update({'picking_id': picking.id})
                    move = move_model.create(move_data)
                    line.move_id = move.id
                    # Create pack to force lot
                    if line.lot_id:
                        operation = pack_model.create({
                            'product_id': line.product_id.id,
                            'product_uom_id': line.product_uom_id.id,
                            'product_qty': line.product_uom_qty,
                            'qty_done': line.product_uom_qty,
                            'location_id': move_data['location_id'],
                            'location_dest_id': move_data['location_dest_id'],
                            'date': datetime.now(),
                            'picking_id': picking.id,
                            })
                        operation_lot.create({
                            'operation_id': operation.id,
                            'qty': line.product_uom_qty,
                            'lot_id': line.lot_id.id,
                        })
                # Set the picking as "To DO" and try to set it as
                # assigned
                picking.action_confirm()
                # Show an error if a picking is not confirmed
                if picking.state != 'confirmed':
                    raise UserError(
                        _('Impossible to create confirmed picking. '
                          'Please Check products availability!'))
                picking.action_assign()
                # Force assign if a picking is not assigned
                if picking.state != 'assigned':
                    picking.force_assign()
                # Show an error if a picking is not assigned
                if picking.state != 'assigned':
                    raise UserError(
                        _('Impossible to create confirmed picking. '
                          'Please Check products availability!'))
                # Add the relation between the new picking
                # and PackagePreparation
                package.picking_ids = [(4, picking.id)]
        return super(StockPickingPackagePreparation, self).action_put_in_pack()
