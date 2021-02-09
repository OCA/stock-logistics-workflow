# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Stock Move Source Relocation",
    "summary": "Change source location of unavailable moves",
    "version": "13.0.1.1.0",
    "development_status": "Alpha",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/wms",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["stock", "stock_helper"],
    "data": ["views/stock_source_relocate_views.xml", "security/ir.model.access.csv"],
}
