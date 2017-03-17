# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# Copyright 2015 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2015 AvanzOsc
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class ProductPackagingTemplate(models.Model):
    _name = 'product.packaging.template'
    _description = 'Product Packaging Template'
    _rec_name = 'packaging_template_name'

    packaging_template_name = fields.Char(required=True)
    package_type = fields.Selection([
        ('unit', 'Unit'),
        ('pack', 'Pack'),
        ('box', 'Box'),
        ('pallet', 'Pallet'),
    ],
        required=True,
    )
    product_tmpl_id = fields.Many2one(
        comodel_name='product.template',
        string='Product',
        index=True,
        ondelete='cascade',
    )
    length = fields.Float(
        digits=dp.get_precision('Stock Weight'),
    )
    length_uom_id = fields.Many2one(
        string='Length Unit',
        comodel_name='product.uom',
        required=True,
        domain=lambda s: [
            ('category_id', '=',
             s.env.ref('product.uom_categ_length').id)
        ],
    )
    width = fields.Float(
        digits=dp.get_precision('Stock Weight'),
    )
    width_uom_id = fields.Many2one(
        string='Width Unit',
        comodel_name='product.uom',
        required=True,
        domain=lambda s: [
            ('category_id', '=',
             s.env.ref('product.uom_categ_length').id)
        ],
    )
    height = fields.Float(
        digits=dp.get_precision('Stock Weight'),
    )
    height_uom_id = fields.Many2one(
        string='Height Unit',
        comodel_name='product.uom',
        required=True,
        domain=lambda s: [
            ('category_id', '=',
             s.env.ref('product.uom_categ_length').id)
        ],
    )
    weight = fields.Float(
        string='Empty Package Weight',
        digits=dp.get_precision('Stock Weight'),
        help='Weight of the empty package.',
    )
    weight_uom_id = fields.Many2one(
        string='Weight Unit',
        comodel_name='product.uom',
        domain=lambda s: [
            ('category_id', '=',
             s.env.ref('product.product_uom_categ_kgm').id)
        ],
    )
    active = fields.Boolean(
        default=True,
    )

    _sql_constraints = [
        ('packaging_template_name_uniq', 'UNIQUE(packaging_template_name)',
         'Template name must be unique.')
    ]

    @api.multi
    def name_get(self):
        names = []
        for rec in self:
            name = '%s [%s x %s x %s]' % (
                rec.packaging_template_name,
                rec.length,
                rec.width,
                rec.height,
            )
            names.append((rec.id, name))
        return names
