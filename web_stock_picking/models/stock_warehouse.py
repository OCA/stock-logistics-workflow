# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'
    barcode_nomenclature_id = fields.Many2one(
        string='Barcode Nomenclature',
        comodel_name='barcode.nomenclature',
        required=True,
        default=lambda s: s.env.ref('barcodes.default_barcode_nomenclature'),
    )
