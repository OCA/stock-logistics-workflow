# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class CannabisTestResult(models.Abstract):

    _name = 'cannabis.test.result'
    _description = 'Cannabis Test Results'

    test_id = fields.Many2one(
        string='Test',
        comodel_name='cannabis.test',
    )
    name = fields.Char(
        compute='_compute_name',
    )
    quantity = fields.Float(
        help='Amount of this terpene that was found in the test.',
    )
    quantity_uom_id = fields.Many2one(
        string='UoM',
        comodel_name='product.uom',
        # Install ``OCA/product-attribute/product_uom`` for this default.
        default=lambda s: s.env.ref(
            'product_uom.product_uom_mg', raise_if_not_found=False,
        ),
        help='Unit of measure for the tested quantity.',
    )
    test_quantity = fields.Float(
        related='test_id.quantity',
    )
    test_quantity_uom_id = fields.Many2one(
        related='test_id.quantity_uom_id',
    )
    quantity_reduced = fields.Float(
        compute='_compute_quantity_reduced',
        help='This is the quantity per 1 unit of tested quantity. For '
             'example, if the total tested quantity was 7 grams and the '
             'result quantity was 93.8 milligrams, this would be 13.4 '
             '(93.8mg / 7g) == (13.4mg / 1g)',
    )

    @api.multi
    def _compute_quantity_reduced(self):
        for record in self:
            record.quantity_reduced = record.quantity / record.test_quantity
