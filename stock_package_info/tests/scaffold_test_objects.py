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
        product = self.env.ref('product.product_product_3')
        production_lot = self.env.ref('stock.lot_icecream_0')
        production_lot.update({
            'product_id': product.id,
        })

        stock_location = self.env.ref('stock.location_inventory')
        company = self.env.ref('base.main_company')

        stock_quant_vals = {
            'company_id': company.id,
            'location_id': stock_location.id,
            'product_id': product.id,
            'name': product['name'],
            'lot_id': production_lot.id,
            'package_id': None,
        }

        if update_vals:
            stock_quant_vals.update(update_vals)
        stock_quant_obj = self.create_stock_quant(stock_quant_vals)
        return stock_quant_obj

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
            'package_type': 'box',
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
            'package_type': 'box',
            'packaging_template_name': self.new_random_name(),
        }

        if update_vals:
            pack_tmpl_vals.update(update_vals)
        return packaging_tmpl.create(pack_tmpl_vals)

    def new_random_name(self, length=10):
        letters = ['a', 'b', 'c', 'd', 'd', 'e', 'f']
        return ''.join(random.choice(letters) for i in range(length))
