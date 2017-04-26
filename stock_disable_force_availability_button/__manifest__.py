# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Disable force availability button",
    "version": "10.0.1.0.0",
    "depends": ["stock"],
    "author": "AvanzOSC,"
              "Tecnativa,"
              "Odoo Community Association (OCA),"
              "Agile Business Group,"
              "Fanha Giang",
    "website": "http://www.odoomrp.com",
    "category": "Warehouse Management",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "data": [
        "security/stock_disable_force_availability_button_security.xml",
        "views/stock_view.xml",
    ],

}
