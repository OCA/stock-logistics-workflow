# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# Copyright 2015 Serv. Tec. Avanzados - Pedro M. Baeza
# Copyright 2015 AvanzOsc
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockPickingPackageTotal(models.Model):
    _name = 'stock.picking.package.total'
    _description = 'Stock Picking Package Total'

    quantity = fields.Integer(
        string='Number of Packages',
    )
    product_pack_tmpl_id = fields.Many2one(
        comodel_name='product.packaging.template',
        string='Logistic Unit',
    )
