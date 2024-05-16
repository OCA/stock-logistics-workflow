# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

{
    "name": "Stock Customer Deposit",
    "summary": "Customer deposits in your warehouse",
    "version": "16.0.1.1.0",
    "development_status": "Alpha",
    "category": "Inventory/Delivery",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["rafaelbn", "EmilioPascual"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale_stock",
    ],
    "excludes": ["stock_owner_restriction"],
    "data": [
        "views/stock_warehouse_views.xml",
        "views/sale_order_views.xml",
        "views/res_partner_views.xml",
        "views/stock_picking_type_views.xml",
    ],
}
