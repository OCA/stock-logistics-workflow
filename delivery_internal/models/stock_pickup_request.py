# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class StockPickupRequest(models.Model):
    _name = 'stock.pickup.request'
    _description = 'Stock Pickup Request'

    name = fields.Char(
        string='Pickup Name',
        default=lambda s: s._default_name(),
    )
    company_id = fields.Many2one(
        string='Responsible Company',
        comodel_name='res.company',
        required=True,
    )
    cash_on_delivery = fields.Boolean()
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('confirmed', 'Confirmed'),
            ('done', 'done')
        ],
        compute='_compute_state',
        store=True,
    )
    picking_id = fields.Many2one(
        string='Source Picking',
        comodel_name='stock.picking',
        required=True,
    )
    in_picking_id = fields.Many2one(
        string='Inbound Buyer Picking',
        comodel_name='stock.picking',
    )
    out_picking_id = fields.Many2one(
        string='Carrier Pickup Picking',
        comodel_name='stock.picking',
    )
    cash_in_picking_id = fields.Many2one(
        string='Cash Picking From Buyer Picking',
        comodel_name='stock.picking',
    )
    cash_out_picking_id = fields.Many2one(
        string='Cash Delivery From Carrier Picking',
        comodel_name='stock.picking',
    )

    def _get_pick_type(self, picking, op_type):
        """ It returns the picking type for the given picking's carrier
        Args:
            picking (stock.picking): The parent picking to use
            op_type (str): Whether we need to stock or cash pick type
        Returns:
            stock.picking.type: The picking type
        """
        return getattr(
            picking.carrier_id,
            'internal_delivery_%s_picking_type_id' % op_type
        )

    def _create_move_lines(self, picking):
        """ It will create move lines based on the given picking
        Args:
            picking (stock.picking): The picking to copy from
        Returns:
            list of stock.move objects
        """
        move_lines = []
        for move_line in picking.move_lines:
            move_lines.append([0, False, {
                'name': move_line.name,
                'product_id': move_line.product_id.id,
                'product_uom': move_line.product_uom.id,
                'product_uom_qty': move_line.product_uom_qty,
                'state': 'draft',
            }])
        return move_lines

    @api.multi
    @api.depends('in_picking_id.state', 'in_picking_id.state')
    def _compute_state(self):
        """ It will compute the status of the pickup based on the delivery
         pickings
         """
        for rec in self:
            state = 'new'
            in_state = rec.in_picking_id.state
            out_state = rec.out_picking_id.state
            if in_state in ('confirmed', 'done') and in_state == out_state:
                state = in_state
            rec.state = state

    @api.multi
    def _default_name(self):
        """ It should return the next sequence for the model to use as a
        name
        Returns:
            str: Sequence code to use as a name
        """
        return self.env['ir.sequence'].next_by_code('stock.pickup.request')

    @api.model
    def write(self, vals):
        """ It will create CoD pickings when CoD is selected in the RFP """
        picking_ids = (
            self.cash_out_picking_id.id, self.cash_in_picking_id.id
        )
        if vals.get('cash_on_delivery') and picking_ids == (False, False):
            pick_type = self._get_pick_type(self.picking_id, 'money')
            in_picking_id = self.env['stock.picking'].create({
                'location_id': pick_type.default_location_src_id.id,
                'location_dest_id': self.picking_id.location_dest_id.id,
                'picking_type_id': pick_type.id,
                'partner_id': self.picking_id.partner_id.id,
                'move_type': 'one',
            })
            out_picking_id = self.env['stock.picking'].create({
                'location_id': self.picking_id.location_id.id,
                'location_dest_id': pick_type.default_location_src_id.id,
                'picking_type_id': pick_type.id,
                'partner_id': self.company_id.partner_id.id,
                'move_type': 'one',
            })
            vals.update({
                'cash_in_picking_id': in_picking_id.id,
                'cash_out_picking_id': out_picking_id.id,
            })
        return super(StockPickupRequest, self).write(vals)

    @api.model
    def create(self, vals):
        """ It should create the pickings for the delivery on create """
        picking = self.env['stock.picking'].browse(vals.get('picking_id'))
        company = self.env['res.company'].browse(vals.get('company_id'))
        pick_type = self._get_pick_type(picking, 'stock')
        move_lines = self._create_move_lines(picking)
        in_picking_id = self.env['stock.picking'].create({
            'location_id': pick_type.default_location_src_id.id,
            'location_dest_id': picking.location_dest_id.id,
            'picking_type_id': pick_type.id,
            'partner_id': picking.partner_id.id,
            'move_type': 'one',
            'move_lines': move_lines,
        })
        out_picking_id = self.env['stock.picking'].create({
            'location_id': picking.location_id.id,
            'location_dest_id': pick_type.default_location_src_id.id,
            'picking_type_id': pick_type.id,
            'partner_id': company.partner_id.id,
            'move_type': 'one',
            'move_lines': move_lines,
        })
        vals.update({
            'in_picking_id': in_picking_id.id,
            'out_picking_id': out_picking_id.id,
        })
        return super(StockPickupRequest, self).create(vals)
