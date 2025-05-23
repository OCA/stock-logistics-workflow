{
    "name": "Stock Picking Purchase Order Alert",
    "version": "14.0.1.0.0",
    "category": "Purchase",
    "summary": "Alert on excessive quantities in purchase receipts",
    "author": "Binhex, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["purchase_stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_picking_type_views.xml",
        "views/stock_picking_views.xml",
        "wizards/stock_picking_alert_wizard.xml",
    ],
    "license": "LGPL-3",
}
