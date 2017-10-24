# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# Copyright 2015 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2015 AvanzOsc
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class ProductPackaging(models.Model):

    _name = 'product.packaging'
    _inherit = ['product.packaging', 'product.packaging.template']

    product_pack_tmpl_id = fields.Many2one(
        name='Product Package Template',
        comodel_name='product.packaging.template',
    )
    layer_qty = fields.Integer(
        string='Package by Layer',
        help='The number of packages by layer',
    )
    rows = fields.Integer(
        string='Number of Layers',
        required=True,
        default=1,
        help='The number of layers on a pallet or box',
    )
    barcode = fields.Char(
        help='The barcode code of the package unit',
    )
    code = fields.Char(
        help='The code of the transport unit',
    )
    weight = fields.Float(
        string='Total Package Weight',
        help='The weight of a full package, pallet or box',
    )
    length = fields.Integer(
        compute='_compute_length',
        inverse='_inverse_length',
        search='_search_length',
    )
    height = fields.Integer(
        compute='_compute_height',
        inverse='_inverse_height',
        search='_search_height',
    )
    width = fields.Integer(
        compute='_compute_width',
        inverse='_inverse_width',
        search='_search_width',
    )

    @api.multi
    def _compute_length(self):
        self._compute_dimension('length')

    @api.multi
    def _inverse_length(self):
        self._inverse_dimension('length')

    @api.model
    def _search_length(self, operator, value):
        self._search_dimension('length', operator, value)

    @api.multi
    def _compute_height(self):
        self._compute_dimension('height')

    @api.multi
    def _inverse_height(self):
        self._inverse_dimension('height')

    @api.model
    def _search_height(self, operator, value):
        self._search_dimension('height', operator, value)

    @api.multi
    def _compute_width(self):
        self._compute_dimension('width')

    @api.multi
    def _inverse_width(self):
        self._inverse_dimension('width')

    @api.model
    def _search_width(self, operator, value):
        self._search_dimension('width', operator, value)

    @api.onchange('product_pack_tmpl_id')
    def _onchange_product_pack_tmpl_id(self):
        """Update the package fields with that of the template."""

        template = self.product_pack_tmpl_id

        for field_name, field in template._fields.iteritems():

            if not any((
                field.compute, field.related, field.automatic,
                field.readonly, field.company_dependent,
                field.name in self.NO_SYNC,
            )):
                self[field_name] = self.product_pack_tmpl_id[field_name]

    @api.multi
    def _compute_dimension(self, attribute):
        for record in self:
            record[attribute] = int(record['%s_float' % attribute])

    @api.multi
    def _inverse_dimension(self, attribute):
        for record in self:
            record['%s_float' % attribute] = float(record[attribute])

    @api.model
    def _search_dimension(self, attribute, operator, value):
        return [('%s_float' % attribute, operator, value)]

