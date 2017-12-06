# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class CannabisTest(models.Model):

    _name = 'cannabis.test'
    _description = 'Cannabis Tests'

    lab_id = fields.Many2one(
        string='Lab',
        help='This is the lab that performed the test.',
        comodel_name='res.partner',
    )
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
    moisture = fields.Float(
        help='Moisture percentage in sample.',
    )
    perform_microbiology = fields.Boolean(
        help='Check this to indicate that the microbiology test was '
             'performed.',
    )
    pass_microbiology = fields.Boolean(
        help='Check this to indicate that the microbiology test was passed.',
    )
    perform_mycotoxin = fields.Boolean(
        help='Check this to indicate that the mycotoxin test was performed.',
    )
    pass_mycotoxin = fields.Boolean(
        help='Check this to indicate that the mycotoxin test was passed.',
    )
    perform_pesticide = fields.Boolean(
        help='Check this to indicate that the pesticide test was performed.',
    )
    pass_pesticide = fields.Boolean(
        help='Check this to indicate that the pesticide test was passed.',
    )
    perform_solvent_residue = fields.Boolean(
        help='Check this to indicate that the solvent residue test was '
             'performed.',
    )
    pass_solvent_residue = fields.Boolean(
        help='Check this to indicate that the solvent residue test was '
             'passed.',
    )
    date_test = fields.Datetime(
        string='Date of Test',
        default=fields.Datetime.now,
    )
    date_expire = fields.Datetime(
        string='Expiration Date',
        help='This is the expiration date of the test results, not of the '
             'item tested.',
    )
    notes = fields.Text()
