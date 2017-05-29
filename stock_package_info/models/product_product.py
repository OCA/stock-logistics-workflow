# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# Copyright 2015 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2015 AvanzOsc
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    weight_net = fields.Float(
        string='Net Weight',
        related='product_tmpl_id.weight_net',
        help='Weight of contents excluding package weight',
    )

    @api.multi
    def write(self, vals):
        weight_net = vals.get('weight_net')
        if weight_net:
            for record in self:
                variants = record.mapped('product_variant_ids').filtered(
                    lambda r: r != record
                )
                super(ProductProduct, variants).write(vals)
        return super(ProductProduct, self).write(vals)
