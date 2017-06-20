# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Stock picking lines with sequence number',
    'version': '9.0.1.0.0',
    'category': 'Warehouse Management',
    'author': "Camptocamp, "
              "Eficent, "
              "Serpent CS, "
              "Odoo Community Association (OCA)",
    'website': 'http://www.camptocamp.com',
    'depends': ['stock', 'sale', 'sale_stock'],
    'data': ['views/stock_view.xml'],
    'installable': True,
    'auto_install': False,
    'license': "AGPL-3",
}
