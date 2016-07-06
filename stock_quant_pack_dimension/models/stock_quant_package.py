# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    length = fields.Float('Length')
    width = fields.Float('Width')
    height = fields.Float('Height')
    dimensional_uom_id = fields.Many2one(
        'product.uom',
        string='Dimensional UoM',
        domain=lambda self: self._get_dimensional_uom_domain(),
        help='UoM for package length, height, width',
    )
    volume = fields.Float(
        string='Volume',
        compute='_calculate_volume',
        store=True,
        readonly=True,
    )

    @api.onchange('length', 'height', 'width', 'dimensional_uom_id')
    def _calculate_volume(self):

        dimensions = [
            self.length,
            self.height,
            self.width,
            self.dimensional_uom_id,
        ]

        if all(dimensions):
            length_m = self._to_meters(self.length, self.dimensional_uom_id)
            height_m = self._to_meters(self.height, self.dimensional_uom_id)
            width_m = self._to_meters(self.width, self.dimensional_uom_id)
            self.volume = length_m * height_m * width_m

    @api.model
    def _to_meters(self, measure, dimensional_uom):
        uom_meters = self.env.ref('product.product_uom_meter')

        return self.env['product.uom']._compute_qty_obj(
            from_unit=dimensional_uom,
            qty=measure,
            to_unit=uom_meters)

    @api.model
    def _get_dimensional_uom_domain(self):
        return [
            ('category_id', '=', self.env.ref('product.uom_categ_length').id)
        ]
