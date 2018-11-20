# -*- coding: utf-8 -*-
# Copyright 2013-2018 Camptocamp SA - Alexandre Fayolle
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, models, fields
from odoo.exceptions import ValidationError
from odoo.addons import decimal_precision as dp


class StockPickingSplit(models.TransientModel):
    _name = 'stock.picking.split'

    picking_id = fields.Many2one(
        'stock.picking',
        string='Picking',
        required=True,
        default=lambda s: s.env.context.get('active_id', False)
    )
    line_ids = fields.One2many(
        'stock.picking.split.line',
        'split_id',
        string='Split Operations',
    )

    @api.model
    def create(self, vals):
        rec = super(StockPickingSplit, self).create(vals)
        rec._generate_lines()
        return rec

    @api.multi
    def process(self):
        self.ensure_one()
        picking = self.picking_id
        if picking.pack_operation_ids:
            reserve = True
            picking.do_unreserve()
        split_picking = picking.copy({
            'name': '/',
            'move_lines': [],
            'pack_operation_ids': [],
            # 'backorder_id': picking.id
            }
        )
        product_split = {}
        for line in self.line_ids:
            product_split[line.product_id] = line.split_qty
        new_move_ids = []
        for move in picking.move_lines:
            if move.state in ('cancel', 'done'):
                continue
            to_split = min(product_split[move.product_id],
                           move.product_uom_qty)
            if to_split > 0:
                product_split[move.product_id] -= to_split
                new_move_ids.append(move.split(to_split))
        self.env['stock.move'].browse(new_move_ids).write(
            {'picking_id': split_picking.id}
        )
        picking.message_post(
            body=_("Split picking <em>%s</em> <b>created</b>.") %
            (split_picking.name)
        )
        split_picking.message_post(
            body=_("Split from picking <em>%s</em> <b>created</b>.") %
            (picking.name)
        )
        split_picking.action_confirm()
        if reserve:
            picking.action_assign()
            split_picking.action_assign()
        return True

    def _generate_lines(self):
        self.ensure_one()
        line_ids = self.env['stock.picking.split.line']
        product_qty = {}
        product_availability = {}
        for move in self.picking_id.move_lines:
            if move.state in ('cancel', 'done'):
                continue
            product = move.product_id
            if product not in product_qty:
                product_qty[product] = move.product_uom_qty
                product_availability[product] = move.reserved_availability
            else:
                product_qty[product] += move.product_uom_qty
                product_availability[product] += move.reserved_availability
        for product, qty in product_qty.items():
            vals = {'picking_id': self.picking_id.id,
                    'product_qty': qty,
                    'split_qty': product_availability[product],
                    'product_id': product.id,
                    'product_uom_id': product.uom_id.id,
                    }
            line_ids |= self.env['stock.picking.split.line'].create(vals)
        self.line_ids = line_ids


class StockPickingSplitLine(models.TransientModel):
    _name = 'stock.picking.split.line'

    split_id = fields.Many2one('stock.picking.split',
                               ondelete='cascade')
    product_id = fields.Many2one(
        'product.product', 'Product', ondelete="cascade", readonly=True
    )
    product_uom_id = fields.Many2one(
        'product.uom', 'Unit of Measure', readonly=True
    )
    product_qty = fields.Float(
        'Total', default=0.0,
        digits=dp.get_precision('Product Unit of Measure'),
        required=True,
        readonly=True
    )
    split_qty = fields.Float(
        'Split', default=0.0,
        digits=dp.get_precision('Product Unit of Measure'), required=True
    )

    @api.constrains('product_qty', 'split_qty')
    def _check_qty(self):
        for rec in self:
            if rec.split_qty > rec.product_qty:
                raise ValidationError(
                    _('Split quantity for product %s must be less than %.3f') %
                    (rec.product_id.name, rec.product_qty)
                )
            if rec.split_qty < 0:
                raise ValidationError(
                    _('Split quantity for product %s must be greater than 0') %
                    (rec.product_id.name)
                )
