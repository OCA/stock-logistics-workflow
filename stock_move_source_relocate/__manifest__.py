# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Stock Move Source Relocation",
    "summary": "Change source location of unavailable moves",
    "version": "18.0.1.0.0",
    "development_status": "Beta",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Camptocamp, BCIM, Odoo Community Association (OCA)",
    "maintainers": ["jbaudoux"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock",
        "stock_location_is_sublocation",
        "stock_route_location_source",
    ],
    "data": ["views/stock_source_relocate_views.xml", "security/ir.model.access.csv"],
}
