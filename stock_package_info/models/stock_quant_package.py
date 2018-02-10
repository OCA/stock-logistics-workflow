# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# Copyright 2015 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2015 AvanzOsc
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    picking_ids = fields.Many2many(
        comodel_name='stock.picking',
        string='Pickings',
        compute='_compute_picking_ids',
    )
    length = fields.Float(
        digits=dp.get_precision('Stock Weight'),
        help='The length of the package',
        related='packaging_id.length_float',
        readonly=True,
    )
    width = fields.Float(
        digits=dp.get_precision('Stock Weight'),
        help='The width of the package',
        related='packaging_id.width_float',
        readonly=True,
    )
    height = fields.Float(
        digits=dp.get_precision('Stock Weight'),
        help='The height of the package',
        related='packaging_id.height_float',
        readonly=True,
    )
    empty_weight = fields.Float(
        string='Empty Package Weight',
        digits=dp.get_precision('Stock Weight'),
        help='Weight of the empty package',
        related='packaging_id.weight',
        readonly=True,
    )
    permitted_volume = fields.Float(
        store=True,
        compute='_compute_permitted_volume',
        digits=dp.get_precision('Stock Weight'),
    )
    total_volume = fields.Float(
        store=True,
        compute='_compute_total_volume',
        digits=dp.get_precision('Stock Weight'),
    )
    total_volume_charge = fields.Float(
        store=True,
        compute='_compute_total_volume_charge',
        digits=dp.get_precision('Stock Weight'),
    )
    total_weight = fields.Float(
        store=True,
        compute='_compute_total_weights',
        help='Total weight of contents including package weight',
        digits=dp.get_precision('Stock Weight'),
    )
    total_weight_net = fields.Float(
        store=True,
        compute='_compute_total_weights',
        help='Total weight of contents excluding package weight',
        digits=dp.get_precision('Stock Weight'),
    )
    total_est_weight = fields.Float(
        string='Total Estimated Weight',
        store=True,
        compute='_compute_total_est_weights',
        digits=dp.get_precision('Stock Weight'),
    )
    total_est_weight_net = fields.Float(
        string='Total Estimated Net Weight',
        store=True,
        compute='_compute_total_est_weight_net',
        digits=dp.get_precision('Stock Weight'),
    )
    real_weight = fields.Float(
        store=True,
        compute='_compute_total_est_weights',
        digits=dp.get_precision('Stock Weight'),
    )
    length_uom_id = fields.Many2one(
        string='Length Unit',
        comodel_name='product.uom',
        related='packaging_id.length_uom_id',
        readonly=True,
    )
    width_uom_id = fields.Many2one(
        string='Width Unit',
        comodel_name='product.uom',
        related='packaging_id.width_uom_id',
        readonly=True,
    )
    height_uom_id = fields.Many2one(
        string='Height Unit',
        comodel_name='product.uom',
        related='packaging_id.height_uom_id',
        readonly=True,
    )
    weight_uom_id = fields.Many2one(
        string='Weight Unit',
        comodel_name='product.uom',
        related='packaging_id.weight_uom_id',
        readonly=True,
    )

    @api.multi
    @api.depends(
        'quant_ids',
        'quant_ids.total_weight',
        'quant_ids.total_weight_net',
    )
    def _compute_total_weights(self):
        for record in self:
            record.total_weight, record.total_weight_net = 0, 0

            for quant_id in record.quant_ids:
                record.total_weight += quant_id.total_weight
                record.total_weight_net += quant_id.total_weight_net

    @api.multi
    @api.depends(
        'total_weight',
        'empty_weight',
        'children_ids',
        'children_ids.total_weight',
        'children_ids.empty_weight',
    )
    def _compute_total_est_weights(self):
        for record in self:
            estim_sum = (
                record.total_weight + record.empty_weight
            )
            for child_id in record.children_ids:
                estim_sum += (
                    child_id.total_weight + child_id.empty_weight
                )
            record.total_est_weight = estim_sum
            record.real_weight = estim_sum

    @api.multi
    @api.depends(
        'total_weight_net',
        'empty_weight',
        'children_ids',
        'children_ids.total_weight_net',
        'children_ids.empty_weight',
    )
    def _compute_total_est_weight_net(self):
        for record in self:
            estim_sum = (
                record.total_weight_net + record.empty_weight
            )
            for child_id in record.children_ids:
                estim_sum += (
                    child_id.total_weight_net + child_id.empty_weight
                )
            record.total_est_weight_net = estim_sum

    @api.multi
    @api.depends('height', 'width', 'length')
    def _compute_permitted_volume(self):
        for record in self:
            record.permitted_volume = (
                record.height * record.width * record.length
            )

    @api.multi
    @api.depends('quant_ids', 'quant_ids.total_volume')
    def _compute_total_volume(self):
        for record in self:
            record.total_volume = 0
            for quant_id in record.quant_ids:
                record.total_volume += quant_id.total_volume

    @api.multi
    @api.depends('total_volume', 'children_ids.total_volume')
    def _compute_total_volume_charge(self):
        for record in self:
            volume_sum = record.total_volume
            for child_id in record.children_ids:
                volume_sum += child_id.total_volume
            record.total_volume_charge = volume_sum

    @api.multi
    def _compute_picking_ids(self):
        for record in self:
            record.picking_ids = self.env['stock.pack.operation'].search(
                [('result_package_id', '=', record.id)]
            ).mapped('picking_id')

    @api.multi
    @api.onchange('packaging_id')
    def onchange_product_packaging_id(self):
        for record in self:
            package = record.packaging_id
            record.length = package.length_float
            record.width = package.width_float
            record.height = package.height_float
            record.empty_weight = package.weight
