# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# Copyright 2015 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2015 AvanzOsc
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class ProductPackaging(models.Model):
    _inherit = 'product.packaging'
    _inherits = {'product.packaging.template': 'product_pack_tmpl_id'}

    layer_qty = fields.Integer(
        string='Package by Layer',
        help='The number of packages by layer',
    )
    rows = fields.Integer(
        string='Number of Layers',
        required=True,
        help='The number of layers on a pallet or box',
    )
    product_pack_tmpl_id = fields.Many2one(
        name='Product Package Template',
        comodel_name='product.packaging.template',
        ondelete='restrict',
        required=True,
    )
    ean = fields.Char(
        string='EAN',
        size=14,
        help='The EAN code of the package unit',
    )
    code = fields.Char(
        help='The code of the transport unit',
    )
    weight = fields.Float(
        string='Total Package Weight',
        help='The weight of a full package, pallet or box',
    )
