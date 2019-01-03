# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductProduct(models.Model):

    _inherit = 'product.product'

    @api.multi
    def write(self, vals):
        if 'standard_price' in vals and self.env.context.get(
                'check_product_moves_date'):
            return self._check_product_move_dates_and_write(vals)
        return super(ProductProduct, self).write(vals)

    @api.multi
    def _get_product_moves_dates_check_domain(self, move_date):
        """
        Get moves in the future of the changed price move date to avoid
        fetching too much records
        :param move_date:
        :return:
        """
        domain = [
            ('product_id', 'in', self.ids),
            ('date', '>', move_date),
            ('move_id.state', '=', 'posted'),
            ('company_id', '=', self.env.user.company_id.id),
        ]
        return domain

    @api.multi
    def _check_product_move_dates_and_write(self, vals):
        """
        Distinguish products that have moves with date > move_date
        to remove standard price modification
        :return:
        """
        move_date = self.env.context.get('move_date')
        products_to_write = self.env['product.product'].browse()
        if move_date:
            move_line_obj = self.env['account.move.line']
            results = move_line_obj.read_group(
                self._get_product_moves_dates_check_domain(move_date),
                ['product_id'],
                ['product_id'],
            )
            products_by_id = []
            for result in results:
                products_by_id.append(result.get('product_id')[0])
            for product in self:
                if product.id not in products_by_id:
                    products_to_write |= product
            super(ProductProduct, products_to_write).write(vals)
        vals.pop('standard_price')
        products = self - products_to_write
        if products:
            return super(ProductProduct, products).write(vals)
        else:
            return True
