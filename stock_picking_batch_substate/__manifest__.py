# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Batch Transfer Sub State",
    "version": "19.0.1.0.0",
    "category": "Tools",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "license": "AGPL-3",
    "depends": [
        # odoo
        "stock_picking_batch",
        # OCA/server-ux
        "base_substate",
    ],
    "data": [
        # Data
        "data/stock_picking_batch_substate_data.xml",
        # Views
        "views/stock_picking_batch_views.xml",
    ],
    "demo": [
        "demo/stock_picking_batch_substate_demo.xml",
    ],
    "installable": True,
}
