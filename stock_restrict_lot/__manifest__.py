{
    "name": "Stock Restrict Lot",
    "summary": "Base module that add back the concept of restrict lot on stock move",
    "version": "16.0.2.0.0",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Akretion, Odoo Community Association (OCA)",
    "maintainers": ["florian-dacosta"],
    "license": "AGPL-3",
    "installable": True,
    "depends": ["stock"],
    "data": ["views/stock_move_views.xml", "views/stock_picking.xml"],
}
