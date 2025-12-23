# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Carrier",
    "version": "17.0.1.0.0",
    "author": "Binhex, Odoo Community Association (OCA)",
    "category": "Inventory/Delivery",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["stock_delivery"],
    "data": [
        "views/stock_picking_type_views.xml",
        "wizard/res_config_settings.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
