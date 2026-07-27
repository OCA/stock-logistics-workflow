# Copyright 2026 Abubakarafghan
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Lot Packing UoM",
    "version": "18.0.1.0.0",
    "category": "stock",
    "summary": "Store packing UoM and received qty on lots; show pack qty on quants",
    "author": "Abubakarafghan, Odoo Community Association (OCA)",
    "maintainers": ["Abubakarafghan"],
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "license": "AGPL-3",
    "development_status": "Beta",
    "images": ["static/description/icon.png"],
    "depends": [
        "purchase_stock",
        "stock_picking_auto_create_lot",
    ],
    "data": [
        "views/stock_lot_views.xml",
        "views/stock_quant_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
