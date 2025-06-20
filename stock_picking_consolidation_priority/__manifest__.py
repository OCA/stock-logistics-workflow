# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Transfers Consolidation Priority",
    "summary": "Raise priority of all transfers for a chain when started",
    "version": "18.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "category": "Stock Management",
    "depends": ["stock", "stock_warehouse_out_pull"],
    "data": ["views/stock_picking_type.xml"],
    "installable": True,
    "license": "AGPL-3",
}
