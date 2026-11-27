# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Picking Type Restrict Location",
    "version": "18.0.1.0.0",
    "development_status": "Beta",
    "category": "Inventory",
    "summary": "Keep the source and destination of transfers inside the "
    "locations of their operation type",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "license": "AGPL-3",
    "depends": ["stock"],
    "data": ["views/stock_picking_type_views.xml"],
    "installable": True,
}
