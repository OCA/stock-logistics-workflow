# -*- coding: utf-8 -*-
# Copyright 2018 Carlos Dauden - Tecnativa <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import _, api, fields, models
from openerp.exceptions import ValidationError


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'

    lot_name = fields.Char(
        string='Lot Name',
        compute='_compute_lot_name',
        inverse='_inverse_lot_name',
    )
    life_date = fields.Datetime(
        string='End of Life Date',
        help='This is the date on which the goods with this Serial Number may '
             'become dangerous and must not be consumed.',
        compute='_compute_life_date',
        inverse='_inverse_life_date',
    )
    lot_track_enabled = fields.Boolean(
        compute='_compute_lot_track_enabled',
    )

    @api.multi
    def _compute_lot_name(self):
        for line in self:
            line.lot_name = ', '.join(
                pl.lot_id.name for pl in line.pack_lot_ids)

    @api.multi
    def _inverse_lot_name(self):
        for line in self:
            lot = line.production_lot_from_name()
            if not lot:
                lot = lot.create({
                    'name': self.lot_name,
                    'product_id': self.product_id.id,
                    'life_date': self.life_date,
                })
            if line.pack_lot_ids:
                if line.pack_lot_ids.lot_id != lot:
                    line.pack_lot_ids.lot_id = lot
            else:
                lot_qty = line.qty_done or line.product_qty
                line.update({
                    'pack_lot_ids': [(0, 0, {
                        'qty_todo': line.product_qty,
                        'qty': lot_qty,
                        'lot_id': lot.id,
                    })],
                    'qty_done': lot_qty,
                })

    @api.multi
    @api.depends('product_id', 'lot_name')
    def _compute_life_date(self):
        for line in self:
            if isinstance(line.id, models.NewId):
                lot = self.env['stock.production.lot'].search([
                    ('product_id', '=', self.product_id.id),
                    ('name', '=', self.lot_name),
                ], limit=1)
                line.life_date = lot.life_date
            else:
                line.life_date = line.pack_lot_ids[:1].lot_id.life_date

    @api.multi
    def _inverse_life_date(self):
        for line in self:
            lot = line.production_lot_from_name()
            if lot and lot.life_date != line.life_date:
                lot.life_date = line.life_date

    @api.multi
    def production_lot_from_name(self):
        StockProductionLot = self.env['stock.production.lot']
        if not self.lot_name:
            if self.pack_lot_ids:
                raise ValidationError(_('Open detail to remove lot'))
            else:
                return StockProductionLot.browse()
        if len(self.pack_lot_ids) > 1:
            raise ValidationError(_('Go to lots to change data'))
        lot = StockProductionLot.search([
            ('product_id', '=', self.product_id.id),
            ('name', '=', self.lot_name),
        ], limit=1)
        return lot

    @api.multi
    @api.depends('product_id')
    def _compute_lot_track_enabled(self):
        for line in self:
            line.lot_track_enabled = bool(line.product_id.tracking != 'none')
