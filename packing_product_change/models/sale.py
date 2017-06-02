# -*- coding: utf-8 -*-
# Copyright 2010-2012, 2017 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, _
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    BASE_TEXT_FOR_OLD_PRD_REPLACE = _(
        "This product replaces partially or completely the ordered product:")

    def _prepare_product_changed(self, vals, product_changed,
                                 account_id=False, ):
        """
        Prepare the invoice line dict when a product has been modified
        this allow to implement custom modification when the product is
        modified in sub modules
        :param dict vals: invoice vals before the modification of the
                          product
        :param int product_changed_id: product id which replaces the original
                                       one
        :param int account_id: optional ID of a G/L account to force
               (this is used for returning products including service)
        :return: dict of values to create() the invoice line
        """

        def get_account_id(product=False, account_id=False):
            if account_id:
                return account_id
            if product:
                account_id = product.property_account_income_id.id
                if not account_id:
                    account_id = product.categ_id.\
                        property_account_income_categ_id.id
                if not account_id:
                    raise UserError(_('Error! Please define income'
                                    'account for this product: "%s" (id:%d).'),
                                    product.name, product.id)
            else:
                prop = self.env['ir.property'].get(
                    'property_account_income_categ', 'product.category')
                account_id = prop.id if prop else False
            return account_id

        product_name = product_changed.name_get()[0][1]
        account_id = get_account_id(
            product=product_changed, account_id=account_id)
        if not account_id:
            raise UserError(
                _('Error! There is no Fiscal Position defined'
                  'or Income category account defined for '
                  'default properties of Product categories.'))

        new_name = '\n'.join([
            product_name,
            self.BASE_TEXT_FOR_OLD_PRD_REPLACE,
            vals['name']])

        return {'product_id': product_changed.id,
                'name': new_name,
                'account_id': account_id, }

    def _prepare_invoice_line(self, qty):

        vals = super(SaleOrderLine, self)._prepare_invoice_line(qty=qty)

        if not vals:
            return vals

        product_changed = False
        # If one of the stock move generated by the SO lines has
        # a product replaced
        for picking in self.order_id.picking_ids:
            for move in picking.move_lines:
                if (move.old_product_id and
                        move.old_product_id != move.product_id):
                    product_changed = move.product_id
                    break

        # we replace the product on the invoice
        # but keep the price of the original product
        if product_changed:
            cur_lang = self.order_id.partner_id.lang
            vals.update(self.with_context(
                lang=cur_lang)._prepare_product_changed(
                vals, product_changed))
        return vals
