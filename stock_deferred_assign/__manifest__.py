# Copyright 2021 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock deferred assign",
    "summary": "Assign/Reserve stock moves when scheduled date "
    "is after today - config days",
    "version": "13.0.1.0.0",
    "development_status": "Beta",
    "category": "Stock",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": ["carlosdauden"],
    "license": "AGPL-3",
    "installable": True,
    "depends": ["procurement_jit"],
    "data": ["views/picking_type.xml"],
}
