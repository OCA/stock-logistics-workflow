# -*- coding: utf-8 -*-
# Copyright 2019 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def get_received_pickings_from_supplier(
            self, supplier_id, warehouse_id, product_ids):
        picking_type_obj = self.env['stock.picking.type']
        move_obj = self.env['stock.move']

        # search for already received pickings
        # from supplier_id and warehouse_id
        picking_type = picking_type_obj.search([
            ('warehouse_id', '=', warehouse_id),
            ('code', '=', 'incoming'),
        ])
        all_received_pickings = self.search([
            ('partner_id', '=', supplier_id),
            ('picking_type_id', '=', picking_type.id),
            ('state', '=', 'done'),
        ], order='date_done DESC')
        moves = move_obj.search([
            ('picking_id', 'in', all_received_pickings.ids),
            ('product_id', 'in', product_ids),
        ])
        received_picking_ids = []
        for picking in all_received_pickings:
            for move in moves:
                if move.picking_id.id == picking.id and\
                        picking.id not in received_picking_ids:
                    received_picking_ids.append(picking.id)
                    break

        received_pickings = self.browse(received_picking_ids)
        return received_pickings

    @api.multi
    def append_returning_move(self, origin_move, product, qty):
        move_obj = self.env['stock.move']

        self.ensure_one()
        if origin_move:
            # The return of a return should be linked with the original's
            # destination move if it was not cancelled
            if origin_move.origin_returned_move_id.move_dest_id.id and\
                    origin_move.origin_returned_move_id.move_dest_id.state !=\
                    'cancel':
                move_dest_id =\
                    origin_move.origin_returned_move_id.move_dest_id.id
            else:
                move_dest_id = False

            new_move = origin_move.copy({
                'product_id': product.id,
                'product_uom_qty': qty,
                'picking_id': self.id,
                'state': 'draft',
                'location_id': origin_move.location_dest_id.id,
                'location_dest_id': origin_move.location_id.id,
                'picking_type_id': self.picking_type_id.id,
                'warehouse_id': self.picking_type_id.warehouse_id.id,
                'origin_returned_move_id': origin_move.id,
                'procure_method': 'make_to_stock',
                'move_dest_id': move_dest_id,
            })
        else:
            new_move = move_obj.create({
                'product_id': product.id,
                'product_uom_qty': qty,
                'picking_id': self.id,
                'state': 'draft',
                'location_id': self.location_id.id,
                'location_dest_id': self.location_dest_id.id,
                'picking_type_id': self.picking_type_id.id,
                'warehouse_id': self.picking_type_id.warehouse_id.id,
                'procure_method': 'make_to_stock',
                'move_dest_id': False,
                'product_uom': product.uom_id.id,
                'name': '[%s] %s' % (product.default_code, product.name),
            })
        return new_move
