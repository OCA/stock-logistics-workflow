# Copyright 2020 Camptocamp (https://www.camptocamp.com)
{
    "name": "Stock Dynamic Routing - Reservation Rules",
    "summary": "Glue module between dynamic routing and reservation rules",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/wms",
    "category": "Warehouse Management",
    "version": "13.0.1.0.1",
    "license": "AGPL-3",
    "depends": [
        "stock_dynamic_routing",  # OCA/wms
        "stock_reserve_rule",  # OCA/stock-logistics-warehouse
    ],
    "data": ["templates/stock_routing_templates.xml", "views/stock_routing_views.xml"],
    "installable": True,
    "auto_install": True,
    "development_status": "Beta",
}
