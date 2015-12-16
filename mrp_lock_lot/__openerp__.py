# -*- coding: utf-8 -*-
# © 2015 Serv. Tec. Avanzados - Pedro M. Baeza (http://www.serviciosbaeza.com)
# © 2015 AvanzOsc (http://www.avanzosc.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "MRP Lock Lot",
    "Summary": "Restrict blocked lots in Manufacturing Orders",
    "version": "8.0.2.0.0",
    "author": "OdooMRP team,"
              "Avanzosc,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza,"
              "Odoo Community Association (OCA)",
    "website": "http://www.odoomrp.com",
    "category": "Manufacturing",
    "depends": [
        "mrp",
        "stock_lock_lot",
    ],
    "data": [
        "wizard/mrp_product_produce_view.xml",
    ],
    "auto_install": True,
    "installable": True,
    "license": "AGPL-3",
    'images': [],
}
