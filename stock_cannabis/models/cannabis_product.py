# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class CannabisProduct(models.Model):

    _name = 'cannabis.product'
    _description = 'Cannabis Products'
    _inherits = {'product.product': 'product_id'}

    strain_id = fields.Many2one(
        string='Strain',
        comodel_name='cannabis.strain',
        required=True,
    )
    type = fields.Selection([
        ('edible', 'Edible'),
        ('extract', 'Extract'),
        ('flower', 'Flower'),
        ('other', 'Other'),
    ],
        default='other',
    )
    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product',
        required=True,
        ondelete='restrict',
    )
    producer_id = fields.Many2one(
        string='Producer',
        comodel_name='res.partner',
    )
    lot_ids = fields.Many2many(
        string='Lots',
        comodel_name='stock.production.lot',
        compute='_compute_lot_ids',
    )
    lot_in_stock_ids = fields.Many2many(
        string='In Stock Lots',
        comodel_name='stock.production.lot',
        compute='_compute_lot_ids',
    )
    content_average_thc = fields.Float(
        string='Average THC',
        compute=lambda s: s._compute_lot_test_average(
            s.lot_in_stock_ids, 'thc', 'content_average_thc',
        ),
        help='Average THC content for all in stock items.',
    )
    content_average_cbd = fields.Float(
        string='Average CBD',
        compute=lambda s: s._compute_lot_test_average(
            s.lot_in_stock_ids, 'cbd', 'content_average_cbd',
        ),
        help='Average CBD content for all in stock items.',
    )
    content_average_cannabis = fields.Float(
        string='Average Cannabis',
        compute=lambda s: s._compute_lot_test_average(
            s.lot_in_stock_ids, 'cannabis', 'content_average_cannabis',
        ),
        help='Average cannabis content for all in stock items.',
    )
    content_average_hash_oil = fields.Float(
        string='Average Hash Oil',
        compute=lambda s: s._compute_lot_test_average(
            s.lot_in_stock_ids, 'hash_oil', 'content_average_hash_oil',
        ),
        help='Average hash oil content for all in stock items.',
    )
    content_historical_thc = fields.Float(
        string='Historical THC',
        compute=lambda s: s._compute_lot_test_average(
            s.lot_ids, 'thc', 'content_historical_thc',
        ),
        help='Historical average of THC content.',
    )
    content_historical_cbd = fields.Float(
        string='Historical CBD',
        compute=lambda s: s._compute_lot_test_average(
            s.lot_ids, 'cbd', 'content_historical_cbd',
        ),
        help='Historical average of CBD content.',
    )
    content_historical_cannabis = fields.Float(
        string='Historical Cannabis',
        compute=lambda s: s._compute_lot_test_average(
            s.lot_ids, 'cannabis', 'content_historical_cannabis',
        ),
        help='Historical average of cannabis content.',
    )
    content_historical_hash_oil = fields.Float(
        string='Historical Hash Oil',
        compute=lambda s: s._compute_lot_test_average(
            s.lot_ids, 'hash_oil', 'content_historical_hash_oil',
        ),
        help='Historical average of hash oil content.',
    )

    @api.multi
    @api.depends('company_id')
    def _compute_lot_ids(self):
        for record in self:
            lots = self.env['stock.production.lot'].search([
                ('product_id', '=', record.id),
                ('company_id', '=', record.company_id.id),
            ])
            in_stock = lots.filtered(lambda r: r.quantity > 0)
            record.lot_ids = [(6, 0, lots.ids)]
            record.lot_in_stock_ids = [(6, 0, in_stock.ids)]

    @api.multi
    def _compute_lot_test_average(self, lots, field_name, save_field):
        """Computes a test average for the fields."""
        for record in self:
            test_results = lots.mapped('cannabis_test_id.%s' % field_name)
            setattr(
                record,
                save_field,
                sum(test_results) / len(test_results),
            )
