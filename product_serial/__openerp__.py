# -*- coding: utf-8 -*-
# © 2008 Raphaël Valyi
# © 2013-2015 Akretion (http://www.akretion.com/) - Alexis de Lattre
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Product Serial",
    "summary": "Enhance Serial Number management",
    "version": "8.0.1.0.0",
    "author": "Akretion,NaN·tic,Odoo Community Association (OCA)",
    "website": "http://www.akretion.com",
    "depends": ["stock"],
    "category": "Inventory, Logistic, Storage",
    "license": "AGPL-3",
    "demo": ["product_demo.xml"],
    "data": [
        "product_view.xml",
        "wizard/prodlot_wizard_view.xml",
    ],
    'installable': True,
}
