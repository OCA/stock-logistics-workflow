# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase
import random


class ScaffoldTestObjects(TransactionCase):
    """ It provides a centralized scaffold for test objects
    Method name prefixes:
        scaffold_: Makes objs to meet Many2one, One2many, Many2many null reqs
        create_: Fills required fields that do not require object creation
        new_: Specific helper methods (e.g. new_random_name())
    """

    def setUp(self):
        super(ScaffoldTestObjects, self).setUp()

    def scaffold_stock_quant_package(self):

        packaging_template_1 = self.create_product_packaging_template()
        stock_quant_package_parent = self.create_stock_quant_package({
            'product_pack_tmpl_id': packaging_template_1.id,
        })
        self.scaffold_stock_quant({
            'package_id': stock_quant_package_parent.id,
        })
        self.scaffold_stock_quant({
            'package_id': stock_quant_package_parent.id,
        })

        packaging_template_2 = self.create_product_packaging_template()
        stock_quant_package_child = self.create_stock_quant_package({
            'product_pack_tmpl_id': packaging_template_2.id,
            'parent_id': stock_quant_package_parent.id,
        })

        self.scaffold_stock_quant({
            'package_id': stock_quant_package_child.id,
        })
        self.scaffold_stock_quant({
            'package_id': stock_quant_package_child.id,
        })

        return {
            'stock_quant_package_parent': stock_quant_package_parent,
            'stock_quant_package_child': stock_quant_package_child,
        }

    def scaffold_stock_quant(self, update_vals=None):
        product_objects = self.scaffold_product()
        product_product_obj = product_objects['product_product_obj']
        production_lot_obj = self.create_stock_production_lot({
            'product_id': product_product_obj.id,
        })

        user_obj = self.create_user()
        company_obj = self.create_company({
            'partner_id': user_obj.id,
        })

        stock_location_obj = self.create_stock_location()

        stock_quant_vals = {
            'company_id': company_obj.id,
            'location_id': stock_location_obj.id,
            'product_id': product_product_obj.id,
            'name': product_product_obj['name'],
            'lot_id': production_lot_obj.id,
            'package_id': None,
        }

        if update_vals:
            stock_quant_vals.update(update_vals)
        stock_quant_obj = self.create_stock_quant(stock_quant_vals)
        return stock_quant_obj

    def scaffold_product(self, update_vals=None):
        product_product_model = self.env['product.product']
        product_template_model = self.env['product.template']

        kilogram = self.env.ref('product.product_uom_kgm')
        name = self.new_random_name()
        prod_categ_obj = self.create_product_category()

        prod_variant_vals = [(
            0, 0,
            {
                'name': name,
                'color': 2,
                'is_product_variant': True,
            },
        )]

        product_template_vals = {
            'name': name,
            'color': 1,
            'categ_id': prod_categ_obj.id,
            'product_variant_ids': prod_variant_vals,
            'packaging_ids': None,
            'tracking': 'lot',
            'type': 'product',
            'uom_id': kilogram.id,
            'uom_po_id': kilogram.id,
            'weight': 20,
            'weight_net': 10,
        }

        if update_vals:
            product_template_vals.update(update_vals)
            prod_variant_vals[0][2].update(update_vals)

        product_template_obj = product_template_model.create(
            product_template_vals
        )
        product_product_vals = {
            'product_tmpl_id': product_template_obj.id,
        }
        product_product_obj = product_product_model.create(
            product_product_vals
        )
        self.inch_id = self.env.ref('product.product_uom_inch')
        self.oz_id = self.env.ref('product.product_uom_oz')
        product_packaging_vals = {
            'name': name,
            'packaging_template_name': name,
            'product_tmpl_id': product_template_obj.id,
            'rows': 1,
            'type': 'box',
            'length': 1,
            'height': 2,
            'width': 3,
            'weight': 4,
            'length_uom_id': self.inch_id.id,
            'height_uom_id': self.inch_id.id,
            'width_uom_id': self.inch_id.id,
            'weight_uom_id': self.oz_id.id,
        }
        product_template_obj.write({
            'packaging_ids': [(
                0, 0,
                product_packaging_vals,
            )]
        })

        return {
            'product_product_obj': product_product_obj,
            'product_template_obj': product_template_obj,
        }

    def create_stock_quant_package(self, update_vals=None):
        quant_package_model = self.env['stock.quant.package']
        name = self.new_random_name()
        pack_template = self.create_product_packaging_template()

        quant_package_vals = {
            'product_pack_tmpl_id': pack_template.id,
            'quant_ids': None,
            'children_ids': None,
            'name': name,
            'parent_id': None,
        }

        if update_vals:
            quant_package_vals.update(update_vals)
        return quant_package_model.create(quant_package_vals)

    def create_stock_quant(self, update_vals=None):
        stock_quant_model = self.env['stock.quant']

        stock_quant_vals = {
            'name': None,
            'company_id': None,
            'location_id': None,
            'product_id': None,
            'qty': 2,
            'volume': 20,
            'weight': 30,
            'weight_net': 20,
            'lot_id': None,
            'package_id': None,
        }

        if update_vals:
            stock_quant_vals.update(update_vals)
        return stock_quant_model.create(stock_quant_vals)

    def create_stock_production_lot(self, update_vals=None):
        lot_model = self.env['stock.production.lot']
        name = self.new_random_name()

        lot_vals = {
            'name': name,
            'product_id': None,
        }

        if update_vals:
            lot_vals.update(update_vals)
        return lot_model.create(lot_vals)

    def create_product_packaging(self, update_vals=None):
        product_packaging_model = self.env['product.packaging']
        self.inch_id = self.env.ref('product.product_uom_inch')
        self.oz_id = self.env.ref('product.product_uom_oz')
        pack_vals = {
            'length': 1,
            'height': 2,
            'width': 3,
            'weight': 4,
            'length_uom_id': self.inch_id.id,
            'height_uom_id': self.inch_id.id,
            'width_uom_id': self.inch_id.id,
            'weight_uom_id': self.oz_id.id,
            'type': 'box',
            'product_tmpl_id': None,
            'rows': 1,
            'name': self.new_random_name(),
            'packaging_template_name': self.new_random_name(),
        }

        if update_vals:
            pack_vals.update(update_vals)
        return product_packaging_model.create(pack_vals)

    def create_product_packaging_template(self, update_vals=None):
        packaging_tmpl = self.env['product.packaging.template']
        self.inch_id = self.env.ref('product.product_uom_inch')
        self.oz_id = self.env.ref('product.product_uom_oz')
        pack_tmpl_vals = {
            'length': 1,
            'height': 2,
            'width': 3,
            'weight': 4,
            'length_uom_id': self.inch_id.id,
            'height_uom_id': self.inch_id.id,
            'width_uom_id': self.inch_id.id,
            'weight_uom_id': self.oz_id.id,
            'type': 'box',
            'packaging_template_name': self.new_random_name(),
        }

        if update_vals:
            pack_tmpl_vals.update(update_vals)
        return packaging_tmpl.create(pack_tmpl_vals)

    def create_product_category(self, update_vals=None):
        product_category_model = self.env['product.category']
        name = self.new_random_name()
        product_category_vals = {
            'name': name,
        }

        if update_vals:
            product_category_vals.update(update_vals)
        return product_category_model.create(product_category_vals)

    def create_company(self, update_vals=None):
        res_company_model = self.env['res.company']
        eur = self.env.ref('base.EUR')
        name = self.new_random_name()

        res_company_vals = {
            'name': name,
            'currency_id': eur.id,
            'partner_id': None,
            'rml_header': 'header',
            'rml_header2': 'header2',
            'rml_header3': 'header3',
            'rml_paper_format': 'a4',
        }

        if update_vals:
            res_company_vals.update(update_vals)
        return res_company_model.create(res_company_vals)

    def create_user(self, update_vals=None):
        res_partner_model = self.env['res.partner']
        name = self.new_random_name()

        res_partner_vals = {
            'notify_email': 'none',
            'name': name,
        }

        if update_vals:
            res_partner_vals.update(update_vals)
        return res_partner_model.create(res_partner_vals)

    def create_stock_location(self, update_vals=None):
        stock_location_model = self.env['stock.location']
        name = self.new_random_name()

        stock_location_vals = {
            'name': name,
            'usage': 'internal',
        }

        if update_vals:
            stock_location_vals.update(update_vals)
        return stock_location_model.create(stock_location_vals)

    def new_random_name(self, length=10):
        letters = ['a', 'b', 'c', 'd', 'd', 'e', 'f']
        return ''.join(random.choice(letters) for i in range(length))
