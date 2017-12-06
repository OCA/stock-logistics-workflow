# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class CannabisTest(models.Model):

    _name = 'cannabis.test'
    _description = 'Cannabis Tests'

    certification_id = fields.Many2one(
        string='Certification',
        comodel_name='cannabis.certification',
    )
    cannabinoid_result_ids = fields.One2many(
        string='Cannabinoid Results',
        comodel_name='cannabis.test.cannabinoid',
        inverse_name='test_id',
    )
    terpene_result_ids = fields.One2many(
        string='Terpene Results',
        comodel_name='cannabis.test.terpene',
        inverse_name='test_id',
    )
    quantity = fields.Float(
        help='Amount that was tested.',
    )
    quantity_uom_id = fields.Many2one(
        string='UoM',
        comodel_name='product.uom',
        default=lambda s: s.env.ref('product.product_uom_gram'),
        help='Unit of measure for the tested quantity.',
    )
