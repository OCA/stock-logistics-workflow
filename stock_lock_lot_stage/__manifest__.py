# Copyright 2025 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Lot Lock Stage",
    "summary": "Manage lot lock status through configurable stages",
    "version": "17.0.1.0.0",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "category": "Warehouse Management",
    "depends": ["stock_lock_lot"],
    "data": [
        "security/ir.model.access.csv",
        "data/stock_lot_stage_data.xml",
        "views/stock_lot_stage_views.xml",
        "views/stock_lot_views.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "license": "AGPL-3",
}
