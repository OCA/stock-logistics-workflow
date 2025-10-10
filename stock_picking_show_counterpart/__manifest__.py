{
    "name": "Stock Picking Show Counterpart",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "summary": """Adds a smart button on stock pickings to view and count related
    pickings (e.g., inter-warehouse transfers).""",
    "author": "BizzAppDev Systems Pvt. Ltd., Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["stock"],
    "data": [
        "views/stock_picking_view.xml",
    ],
    "installable": True,
}
