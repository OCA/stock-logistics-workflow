# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPickingFillPartnerReference(models.TransientModel):

    _name = 'stock.picking.fill.partner.reference'

    name = fields.Char()
    same_ref = fields.Boolean(
        string='Put the same reference on every move'
    )
    reference = fields.Char()
    move_line_ids = fields.One2many(
        'stock.picking.fill.partner.reference.line',
        'wizard_id',
        string='Moves',
    )

    @api.model
    def _prepare_move_lines(self, picking):
        move_lines = []
        for move in picking.move_lines:
            line = {
                'move_line_id': move.id,
                'product_id': move.product_id.id,
                'product_uom_qty': move.product_uom_qty,
                'existing_reference': move.partner_reference,
            }
            move_lines.append(line)
        return {'move_line_ids': move_lines}

    @api.model
    def default_get(self, fields):
        res = super(StockPickingFillPartnerReference, self).default_get(
            fields)
        active_id = self.env.context.get('active_id')
        active_model = self.env.context.get('active_model')
        if active_id and active_model and active_model == 'stock.picking':
            picking = self.env['stock.picking'].browse(active_id)
            lines = self._prepare_move_lines(picking)
            res.update(lines)
        res = self._convert_to_write(self._convert_to_cache(res))
        return res

    @api.multi
    def _write_partner_reference(self):
        self.ensure_one()
        if self.same_ref:
            self.move_line_ids.mapped('move_line_id').write({
                'partner_reference': self.reference,
            })
        else:
            for move in self.move_line_ids:
                move.move_line_id.write({
                    'partner_reference': move.reference
                })

    @api.multi
    def doit(self):
        for wizard in self:
            wizard._write_partner_reference()
        return


class StockPickingFillPartnerReferenceLine(models.TransientModel):

    _name = 'stock.picking.fill.partner.reference.line'

    wizard_id = fields.Many2one(
        'stock.picking.fill.partner.reference',
    )
    move_line_id = fields.Many2one(
        'stock.move',
        string='Move',
    )
    product_id = fields.Many2one(
        related='move_line_id.product_id',
        readonly=True,
    )
    product_uom_qty = fields.Float(
        related='move_line_id.product_uom_qty',
        readonly=True,
    )
    existing_reference = fields.Char(
        related='move_line_id.partner_reference',
        readonly=True,
    )
    reference = fields.Char()
