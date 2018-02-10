# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# Copyright 2015-2018 Tecnativa - Pedro M. Baeza
# Copyright 2015 AvanzOsc
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    weight_net = fields.Float(
        string='Net Weight',
        help='Weight of contents excluding package weight',
        digits=dp.get_precision('Stock Weight'),
        compute='_compute_weight_net',
        inverse='_inverse_weight_net',
        store=True,
    )

    @api.depends('product_variant_ids', 'product_variant_ids.weight_net')
    def _compute_weight_net(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1
        )
        for template in unique_variants:
            template.weight_net = template.product_variant_ids.weight_net
        for template in (self - unique_variants):
            template.weight_net = 0.0

    def _inverse_weight_net(self):
        for tmpl in self:
            if len(tmpl.product_variant_ids) == 1:
                tmpl.product_variant_ids.weight_net = tmpl.weight_net

    @api.model
    def create(self, vals):
        template = super(ProductTemplate, self).create(vals)
        # This is needed to set given values to first variant after creation
        related_vals = {}
        if vals.get('weight_net'):
            related_vals['weight_net'] = vals['weight_net']
        if related_vals:
            template.write(related_vals)
        return template
