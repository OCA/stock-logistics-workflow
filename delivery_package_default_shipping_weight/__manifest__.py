# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Delivery Package Default Shipping Weight",
    "summary": "Set default package shipping weight according to packaging",
    "version": "18.0.1.0.0",
    "development_status": "Production/Stable",
    "category": "Inventory",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["stock_delivery"],
    "data": ["views/stock_package_type_views.xml"],
}
