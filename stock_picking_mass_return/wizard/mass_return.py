# -*- coding: utf-8 -*-
# Copyright 2019 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp


class MassReturnLineWizard(models.TransientModel):
    _name = 'mass.return.line.wizard'

    mass_return_id = fields.Many2one(
        'mass.return.wizard'
    )

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True
    )
    product_qty = fields.Float(
        "Quantity", digits=dp.get_precision('Product Unit of Measure'),
        required=True)


class MassReturnWizard(models.TransientModel):
    _name = 'mass.return.wizard'

    supplier_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        domain=[('supplier', '=', True)],
        required=True
    )

    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        required=True
    )

    return_line_ids = fields.One2many(
        'mass.return.line.wizard', 'mass_return_id',
        string='Products to return'
    )

    @api.multi
    def _create_picking_to_return(
            self, received_pickings, supplier, warehouse):
        picking_obj = self.env['stock.picking']

        if received_pickings:
            # create new picking for returned products
            received_picking = received_pickings[0]
            picking_type_id = \
                received_picking.picking_type_id.return_picking_type_id.id or\
                received_picking.picking_type_id.id
            new_picking = received_picking.copy({
                'move_lines': [],
                'picking_type_id': picking_type_id,
                'state': 'draft',
                'origin': received_picking.name,
                'location_id': received_picking.location_dest_id.id,
                'location_dest_id': received_picking.location_id.id})
            new_picking.message_post_with_view(
                'mail.message_origin_link',
                values={'self': new_picking, 'origin': received_picking},
                subtype_id=self.env.ref('mail.mt_note').id)
        else:
            new_picking = picking_obj.create({
                'partner_id': supplier.id,
                'move_lines': [],
                'picking_type_id': warehouse.out_type_id.id,
                'state': 'draft',
                'origin': False,
                'location_id': warehouse.lot_stock_id.id,
                'location_dest_id': self.env.ref(
                    'stock.stock_location_suppliers').id,
            })

        return new_picking

    @api.multi
    def return_products(self):
        picking_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']

        self.ensure_one()
        supplier_id = self.supplier_id.id
        warehouse_id = self.warehouse_id.id
        product_ids = []
        for line in self.return_line_ids:
            if line.product_qty and line.product_id.id not in product_ids:
                product_ids.append(line.product_id.id)

        received_pickings = picking_obj.get_received_pickings_from_supplier(
            supplier_id, warehouse_id, product_ids)

        returning_picking = self._create_picking_to_return(
            received_pickings, self.supplier_id, self.warehouse_id)

        for return_line in self.return_line_ids:
            first_move = False
            qty_to_return = return_line.product_qty
            if qty_to_return <= 0:
                break
            for received_picking in received_pickings:
                if qty_to_return <= 0:
                    break
                received_moves = move_obj.search([
                    ('picking_id', '=', received_picking.id),
                    ('product_id', '=', return_line.product_id.id),
                    ('state', '=', 'done'),
                ])
                for received_move in received_moves:
                    # check available quantity to return:
                    current_qty =\
                        received_move.get_available_quantity_to_return()
                    current_qty = min(current_qty, qty_to_return)
                    if current_qty <= 0:
                        continue

                    current_move = returning_picking.append_returning_move(
                        received_move, received_move.product_id, current_qty)
                    if not first_move:
                        first_move = current_move

                    qty_to_return -= current_qty
                    if qty_to_return <= 0:
                        break
            if qty_to_return:
                if first_move:
                    # Partial return:
                    first_move.write({
                        'product_uom_qty': first_move.product_uom_qty +
                        return_line.product_id.uom_id._compute_quantity(
                            qty_to_return, first_move.product_uom,
                            rounding_method='HALF-UP'),
                        'ordered_qty': first_move.ordered_qty + qty_to_return,
                    })
                else:
                    returning_picking.append_returning_move(
                        False, return_line.product_id, qty_to_return)
        returning_picking.action_confirm()
        returning_picking.action_assign()

        return {
            "view_type": "form",
            "view_mode": "form",
            "res_model": 'stock.picking',
            "res_id": returning_picking.id,
            "target": "current",
            "type": "ir.actions.act_window",
        }
