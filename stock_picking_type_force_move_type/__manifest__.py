# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Stock Picking Type Force Shipping Policy",
    "summary": "Force shipping policies on operation types",
    "version": "18.0.1.0.1",
    "development_status": "Production/Stable",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["stock"],
    "data": ["views/stock_picking_type.xml"],
    "post_init_hook": "post_init_hook",
}
