# Copyright 2015 Serv. Tec. Avanzados - Pedro M. Baeza (http://www.serviciosbaeza.com)
# Copyright 2015 AvanzOsc (http://www.avanzosc.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Lock Lot",
    "Summary": "Restrict blocked lots in Stock Moves and reservations",
    "version": "13.0.1.0.0",
    "author": "Avanzosc, "
    "Serv. Tecnol. Avanzados - Pedro M. Baeza, "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "category": "Warehouse Management",
    "depends": ["stock", "product"],
    "data": [
        "security/stock_lock_lot_security.xml",
        "data/stock_lock_lot_data.xml",
        "views/product_category_view.xml",
        "views/stock_production_lot_view.xml",
        "views/stock_location_view.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
    "images": [],
}
