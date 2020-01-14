# Copyright 2020 Studio73 - Guillermo Llinares <guillermo@studio73.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Batch back2draft",
    "summary": "Reopen cancelled picking batches",
    "version": "12.0.1.0.0",
    "category": "Warehouse Management",
    'website': 'https://github.com/OCA/stock-logistics-workflow',
    "author": "Studio73, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["stock_picking_batch", "stock_picking_back2draft"],
    "data": ["views/stock_picking_batch_view.xml"],
    "auto_install": True,
    "installable": True,
}
