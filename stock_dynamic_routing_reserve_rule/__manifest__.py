# Copyright 2020 Camptocamp (https://www.camptocamp.com)
{
    "name": "Stock Dynamic Routing - Reservation Rules",
    "summary": "Glue module between dynamic routing and reservation rules",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "category": "Warehouse Management",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "depends": [
        "stock_dynamic_routing",  # OCA/stock-logistics-workflow
        "stock_reserve_rule",  # OCA/stock-logistics-reservation
    ],
    "data": ["templates/stock_routing_templates.xml", "views/stock_routing_views.xml"],
    "installable": True,
    "auto_install": True,
    "development_status": "Beta",
}
