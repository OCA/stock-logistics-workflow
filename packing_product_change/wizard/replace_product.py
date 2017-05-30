# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields
# from openerp.osv import orm, fields


class replace_product(models.TransientModel):

    _name = "replace.product"
    _description = "Replace Product"

    product_id = fields.Many2one(
        'product.product',
        'Replace by product',
        required=True,
        help="Choose which product will replace the original one.")

    def replace(self):
        rec_id = self.env.context.get('active_id')
        replacement_product = self.product_id
        move = self.env['stock.move'].browse(rec_id)
        move.replace_product(replacement_product.id)
        return{'type': 'ir.actions.act_window_close'}
