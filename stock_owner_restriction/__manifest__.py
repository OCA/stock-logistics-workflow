# Copyright 2020 Carlos Dauden - Tecnativa
# Copyright 2020 Sergio Teruel - Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Owner Restriction",
    "summary": "Do not reserve quantity with assigned owner",
    "version": "14.0.1.0.1",
    "development_status": "Beta",
    "category": "stock",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "data": ["views/stock_picking_type_views.xml", "views/stock_picking_views.xml"],
    "depends": ["stock"],
    "post_init_hook": "set_default_owner_restriction",
    "uninstall_hook": "uninstall_hook",
}
