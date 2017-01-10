# -*- coding: utf-8 -*-
#    Author: Francesco Apruzzese
#    Copyright 2015 Apulia Software srl
#    Copyright 2015 Lorenzo Battistini - Agile Business Group
#    Copyright 2016 Alessio Gerace - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class StockPickingPackagePreparationLine(models.Model):

    _name = 'stock.picking.package.preparation.line'
    _description = 'Package Preparation Line'
    _order = 'sequence asc'

    package_preparation_id = fields.Many2one(
        'stock.picking.package.preparation', string='Package Preparation',
        ondelete='cascade', required=True)
    name = fields.Text(string='Description', required=True)
    move_id = fields.Many2one('stock.move', string='Stock Move',
                              ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product')
    product_uom_qty = fields.Float(
        digits=dp.get_precision('Product Unit of Measure'),
        string="Quantity",
        help="If you change this quantity for a 'ready' picking, the system "
             "will not generate a back order, but will just deliver the new "
             "quantity")
    product_uom_id = fields.Many2one('product.uom', string="UoM")
    lot_id = fields.Many2one('stock.production.lot', 'Lot')
    sequence = fields.Integer(default=10)
    note = fields.Text()

    @api.multi
    def write(self, values):
        super(StockPickingPackagePreparationLine, self).write(values)
        if 'product_uom_qty' in values and self.move_id:
            if self.move_id.product_uom_qty != values['product_uom_qty']:
                # perform a new reservation with the new quantity
                move_context = self.move_id.with_context(
                    skip_update_line_ids=True)
                move_context.picking_id.do_unreserve()
                move_context.product_uom_qty = values['product_uom_qty']
                move_context.picking_id.action_assign()

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            name = self.product_id.name_get()
            if name:
                self.name = name[0][1]
            self.product_uom_id = self.product_id.uom_id.id

    @api.model
    def _prepare_lines_from_pickings(self, picking_ids):
        lines = []
        if not picking_ids:
            return lines
        picking_model = self.env['stock.picking']
        for picking in picking_model.browse(picking_ids):
            for move_line in picking.move_lines:
                # If stock move is cancel, don't create package
                # preparation line
                if move_line.state == 'cancel':
                    continue
                # search if the move is related with a
                # PackagePreparationLine, yet. If not, create a new line
                if not self.search([('move_id', '=', move_line.id)],
                                   count=True):
                    lines.append({
                        'move_id': move_line.id,
                        'name': move_line.name,
                        'product_id': move_line.product_id.id,
                        'product_uom_qty': move_line.product_uom_qty,
                        'product_uom_id': move_line.product_uom.id,
                        'lot_id': move_line.restrict_lot_id.id
                        if move_line.restrict_lot_id else False,
                        })
        return lines

    @api.multi
    def get_move_data(self):
        self.ensure_one()
        return {
            'name': self.name,
            'product_id': self.product_id.id,
            'product_uom_qty': self.product_uom_qty,
            'product_uom': self.product_uom_id.id,
            'restrict_lot_id': self.lot_id.id
            if self.lot_id else False,
            }
