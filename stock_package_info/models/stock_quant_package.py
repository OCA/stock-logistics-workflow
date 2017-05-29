# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# Copyright 2015 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2015 AvanzOsc
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from openerp.addons import decimal_precision as dp

import logging
_logger = logging.getLogger(__name__)


class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    picking_ids = fields.Many2many(
        comodel_name='stock.picking',
        string='Pickings',
        compute='_compute_picking_ids',
    )
    product_pack_tmpl_id = fields.Many2one(
        comodel_name='product.packaging.template',
        string='Packaging Template',
    )
    length = fields.Float(
        digits=dp.get_precision('Stock Weight'),
        help='The length of the package',
    )
    width = fields.Float(
        digits=dp.get_precision('Stock Weight'),
        help='The width of the package',
    )
    height = fields.Float(
        digits=dp.get_precision('Stock Weight'),
        help='The height of the package',
    )
    empty_weight = fields.Float(
        string='Empty Package Weight',
        digits=dp.get_precision('Stock Weight'),
        help='Weight of the empty package'
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

    @api.multi
    @api.depends(
        'quant_ids',
        'quant_ids.total_weight',
        'quant_ids.total_weight_net',
    )
    def _compute_total_weights(self):
        for rec_id in self:
            rec_id.total_weight, rec_id.total_weight_net = 0, 0

            for quant_id in rec_id.quant_ids:
                rec_id.total_weight += quant_id.total_weight
                rec_id.total_weight_net += quant_id.total_weight_net

    @api.multi
    @api.depends(
        'total_weight',
        'empty_weight',
        'children_ids',
        'children_ids.total_weight',
        'children_ids.empty_weight',
    )
    def _compute_total_est_weights(self):
        for rec_id in self:
            estim_sum = (
                rec_id.total_weight + rec_id.empty_weight
            )
            for child_id in rec_id.children_ids:
                estim_sum += (
                    child_id.total_weight + child_id.empty_weight
                )
            rec_id.total_est_weight = estim_sum
            rec_id.real_weight = estim_sum

    @api.multi
    @api.depends(
        'total_weight_net',
        'empty_weight',
        'children_ids',
        'children_ids.total_weight_net',
        'children_ids.empty_weight',
    )
    def _compute_total_est_weight_net(self):
        for rec_id in self:
            estim_sum = (
                rec_id.total_weight_net + rec_id.empty_weight
            )
            for child_id in rec_id.children_ids:
                estim_sum += (
                    child_id.total_weight_net + child_id.empty_weight
                )
            rec_id.total_est_weight_net = estim_sum

    @api.multi
    @api.depends('height', 'width', 'length')
    def _compute_permitted_volume(self):
        for rec_id in self:
            rec_id.permitted_volume = (
                rec_id.height * rec_id.width * rec_id.length
            )

    @api.multi
    @api.depends('quant_ids', 'quant_ids.total_volume')
    def _compute_total_volume(self):
        for rec_id in self:
            rec_id.total_volume = 0
            for quant_id in rec_id.quant_ids:
                rec_id.total_volume += quant_id.total_volume

    @api.multi
    @api.depends('total_volume', 'children_ids.total_volume')
    def _compute_total_volume_charge(self):
        for rec_id in self:
            volume_sum = rec_id.total_volume
            for child_id in rec_id.children_ids:
                volume_sum += child_id.total_volume
            rec_id.total_volume_charge = volume_sum

    @api.multi
    def _compute_picking_ids(self):
        for rec_id in self:
            rec_id.picking_ids = self.env['stock.pack.operation'].search(
                [('result_package_id', '=', rec_id.id)]
            ).mapped('picking_id')

    @api.multi
    @api.onchange('product_pack_tmpl_id')
    def onchange_product_pack_tmpl_id(self):
        for rec_id in self:
            tmpl = rec_id.product_pack_tmpl_id
            rec_id.length = tmpl.length
            rec_id.width = tmpl.width
            rec_id.height = tmpl.height
            rec_id.empty_weight = tmpl.weight

    @api.model
    def create(self, vals):
        if vals.get('product_pack_tmpl_id', False):
            tmpl = self.env['product.packaging.template'].browse(
                vals.get('product_pack_tmpl_id')
            )
            vals.update({
                'length': tmpl.length,
                'width': tmpl.width,
                'height': tmpl.height,
                'empty_weight': tmpl.weight,
            })
        return super(StockQuantPackage, self).create(vals)
