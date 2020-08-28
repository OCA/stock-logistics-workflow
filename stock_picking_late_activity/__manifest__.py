# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Picking Late Activity",
    "summary": "Add an scheduled action that creates late picking activities",
    "version": "12.0.1.0.0",
    "development_status": "Production/Stable",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": ["ernestotejeda"],
    "license": "AGPL-3",
    "depends": [
        "stock",
    ],
    "data": [
        "data/ir_cron_data.xml",
        "data/mail_activity_type_data.xml",
        "views/stock_picking_views.xml",
    ],
}
