# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Batch Creation",
    "summary": """
        Create a batch of pickings to be processed all together""",
    "version": "18.0.1.1.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "category": "Warehouse Management",
    "application": False,
    "installable": True,
    "depends": [
        "delivery",  # weight on picking
        "stock_picking_batch",
        "stock_picking_volume",  # OCA/stock-logistics-warehouse
        "stock_split_picking_dimension",
    ],
    "data": [
        "views/stock_device_type.xml",
        "views/stock_picking_batch.xml",
        "views/stock_picking.xml",
        "wizards/make_picking_batch.xml",
        "security/ir.model.access.csv",
    ],
    "assets": {
        "web.assets_backend": [
            "stock_picking_batch_creation/static/src/**/*.js",
        ],
    },
    "development_status": "Beta",
    "maintainers": ["lmignon"],
    "pre_init_hook": "pre_init_hook",
}
