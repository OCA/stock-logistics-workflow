# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Joel Grand-Guillaume, Guewen Baconnier
#    Copyright 2010-2014 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

# from openerp.osv import orm
# from openerp.tools.translate import _

from odoo import fields, models, _
from odoo.exceptions import UserError

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

# class sale_order_line(orm.Model):
#     _inherit = 'sale.order.line'

    BASE_TEXT_FOR_OLD_PRD_REPLACE = _(
        "This product replaces partially or completely the ordered product:")

    def _prepare_product_changed(self, vals, product_changed_id,
                                 account_id=False, ):
        """
        Prepare the invoice line dict when a product has been modified
        this allow to implement custom modification when the product is
        modified in sub modules
        :param browse_record line; sale.order.line record to invoice
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
                account_id = product.property_account_income.id
                if not account_id:
                    account_id = product.categ_id.\
                        property_account_income_categ.id
                if not account_id:
                    raise UserError('Error! Please define income'
                                    'account for this product: "%s" (id:%d).',
                                    product.name, product.id)
            else:
                prop = self.env['ir.property'].get(
                    'property_account_income_categ', 'product.category')
                account_id = prop.id if prop else False
            return account_id

        prod_obj = self.env['product.product']
        product_name = prod_obj.name_get(product_changed_id)
        product_changed = prod_obj.browse(product_changed_id)
        account_id = get_account_id(
            product=product_changed, account_id=account_id)
        if not account_id:
            raise UserError('Error! There is no Fiscal Position defined'
                'or Income category account defined for default properties of '
                'Product categories.')

        new_name = '\n'.join([product_name,
                                      self.BASE_TEXT_FOR_OLD_PRD_REPLACE,
                                      vals['name']])

        return {'product_id': product_changed_id,
                        'name': new_name,
                        'account_id': account_id,
                        }

    # def _prepare_product_changed(self, cr, uid, line, vals, product_changed_id,
    #                              account_id=False, context=None):
    #     """
    #     Prepare the invoice line dict when a product has been modified
    #     this allow to implement custom modification when the product is
    #     modified in sub modules
    #
    #     :param browse_record line; sale.order.line record to invoice
    #     :param dict vals: invoice vals before the modification of the
    #                       product
    #     :param int product_changed_id: product id which replaces the original
    #                                    one
    #     :param int account_id: optional ID of a G/L account to force
    #            (this is used for returning products including service)
    #     :return: dict of values to create() the invoice line
    #     """
    #     def get_account_id(product=False, account_id=False):
    #         if account_id:
    #             return account_id
    #         if product:
    #             account_id = product.property_account_income.id
    #             if not account_id:
    #                 account_id = product.categ_id.\
    #                     property_account_income_categ.id
    #             if not account_id:
    #                 raise orm.except_orm(
    #                     _('Error!'),
    #                     _('Please define income account for '
    #                       'this product: "%s" (id:%d).') %
    #                     (product.name, product.id))
    #         else:
    #             prop = self.pool.get('ir.property').get(
    #                 cr, uid,
    #                 'property_account_income_categ', 'product.category',
    #                 context=context)
    #             account_id = prop.id if prop else False
    #         return account_id
    #
    #     prod_obj = self.pool.get('product.product')
    #
    #     product_name = prod_obj.name_get(
    #         cr, uid, [product_changed_id], context=context)[0][1]
    #
    #     product_changed = prod_obj.browse(
    #         cr, uid, product_changed_id, context=context)
    #     account_id = get_account_id(
    #         product=product_changed, account_id=account_id)
    #
    #     if not account_id:
    #         raise orm.except_orm(
    #             _('Error!'),
    #             _('There is no Fiscal Position defined or Income '
    #               'category account defined for default properties of '
    #               'Product categories.'))
    #
    #     new_name = '\n'.join([product_name,
    #                           self.BASE_TEXT_FOR_OLD_PRD_REPLACE,
    #                           vals['name']])
    #
    #     return {'product_id': product_changed_id,
    #             'name': new_name,
    #             'account_id': account_id,
    #             }



    def _prepare_invoice_line(self, qty):

        context = self._context or {}
        vals = super(sale_order_line)._prepare_invoice_line(
            self, qty=qty)

        if not vals:
            return vals

        product_changed_id = False
        # If one of the stock move generated by the SO lines has
        # a product replaced
        for move in line.move_ids:
            if move.old_product_id and move.old_product_id != move.product_id:
                product_changed_id = move.product_id.id
                break

        # we replace the product on the invoice
        # but keep the price of the original product
        if product_changed_id:
            partner_obj = self.env['res.partner']
            ctx = self.env.context.copy()
            lang = partner_obj.browse(self.order_id.partner_id.id,).lang
            ctx.update({'lang': lang})
            self.env.context = ctx
            vals.update(self._prepare_product_changed(
                vals, product_changed_id))

        return vals

    # def _prepare_order_line_invoice_line(self, cr, uid, line,
    #                                      account_id=False, context=None):
    #     """Prepare the dict of values to create the new invoice line for a
    #        sale order line. This method may be overridden to implement custom
    #        invoice generation (making sure to call super() to establish
    #        a clean extension chain).
    #
    #        Override the method to add an invoice line with the replaced
    #        product in the related packing
    #        Keep the price of the original product but use the accounts of the
    #        replacement product
    #        Add a comment which indicates the modification
    #
    #        :param browse_record line: sale.order.line record to invoice
    #        :param int account_id: optional ID of a G/L account to force
    #            (this is used for returning products including service)
    #        :return: dict of values to create() the invoice line
    #     """
    #     if context is None:
    #         context = {}
    #     vals = super(sale_order_line, self)._prepare_order_line_invoice_line(
    #         cr, uid, line, account_id=account_id, context=context)
    #
    #     if not vals:
    #         return vals
    #
    #     product_changed_id = False
    #     # If one of the stock move generated by the SO lines has
    #     # a product replaced
    #     for move in line.move_ids:
    #         if move.old_product_id and move.old_product_id != move.product_id:
    #             product_changed_id = move.product_id.id
    #             break
    #
    #     # we replace the product on the invoice
    #     # but keep the price of the original product
    #     if product_changed_id:
    #         partner_obj = self.pool['res.partner']
    #         ctx = context.copy()
    #         lang = partner_obj.browse(
    #             cr, uid, line.order_id.partner_id.id,
    #             context=context).lang
    #         ctx['lang'] = lang
    #
    #         vals.update(self._prepare_product_changed(
    #             cr, uid, line, vals, product_changed_id,
    #             account_id=account_id, context=ctx))
    #
    #     return vals
