# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    property_cost_method = fields.Selection(
        selection_add=[('last', 'Last Price')])


class ProductCategory(models.Model):
    _inherit = 'product.category'

    property_cost_method = fields.Selection(
        selection_add=[('last', 'Last Price')])
