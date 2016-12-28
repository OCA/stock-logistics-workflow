# -*- coding: utf-8 -*-
# © 2015 Serv. Tec. Avanzados - Pedro M. Baeza (http://www.serviciosbaeza.com)
# © 2015 AvanzOsc (http://www.avanzosc.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Lock Lot",
    "Summary": "Restrict blocked lots in Stock Moves and reservations",
    "version": "8.0.2.0.0",
    "author": "OdooMRP team,"
              "Avanzosc,"
              "Serv. Tecnol. Avanzados - Pedro M. Baeza,"
              "Odoo Community Association (OCA)",
    "website": "http://www.odoomrp.com",
    "category": "Warehouse Management",
    "depends": ["stock",
                "product",
                ],
    "data": [
        "security/stock_lock_lot_security.xml",
        "data/stock_lock_lot_data.xml",
        "wizard/stock_transfer_details_view.xml",
        "wizard/wiz_lock_lot_view.xml",
        "views/product_category_view.xml",
        "views/stock_production_lot_view.xml",
        "views/stock_quant_view.xml",
        "views/res_config_view.xml",
        "views/stock_location_view.xml"
    ],
    "installable": True,
    "license": "AGPL-3",
    'images': [],
}
