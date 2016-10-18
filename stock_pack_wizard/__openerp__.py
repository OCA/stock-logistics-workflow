# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 Elico Corp (<http://www.elico-corp.com>)
#    Alex Duan <alex.duan@elico-corp.com>
#    Jon Chow <jon.chow@elico-corp.com>
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

{
    'name': 'Stock Pack Wizard',
    'version': '1.0',
    'author': 'Elico Corp,Odoo Community Association (OCA)',
    'website': 'http://www.elico-corp.com',
    'summary': '',
    'description': """
 .. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License

Stock Packing Wizard
====================

Add a new wizard on stock picking to easily assign different stock moves
into package.

Installation
============

This module depends on **sale_stock** and **report_webkit** modules.

Usage
=====
To use this module, you need to:

* The current user should belong to the group:
* Go to Settings > Warehosue >
    "Track serial number on logistic units (pallets)"
* Go to Warehosue > delivery order
    (state is in 'draft','assigned','auto','confirmed').

    In the form, you can find a new button **New Pack** which allows you
    packing moves together and quantity you want.
* The default package template in the wizard is the one latest used.

Contributors
------------

* Alex Duan: alex.duan@elico-corp.com / duanyp91@gmail.com

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization
    whose mission is to support the collaborative development of Odoo features
        and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
This module add new functionalities to Pack:
    """,
    # depends on sale_stock to have the field:sale_id from stock.picking model.
    'depends': ['sale_stock', 'report_webkit'],
    'category': '',
    'sequence': 10,
    'demo': [],
    'data': [
        'product_ul_view.xml',
        'stock_tracking_view.xml',
        'wizard/wizard_picking_tracking_view.xml',
        'stock_picking_view.xml',
        'stock_tracking_report.xml',
        'data/product.ul.csv',
    ],
    'test': ['test/test_pack_wizard.yml'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'css': [],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
