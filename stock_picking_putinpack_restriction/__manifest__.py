# Copyright 2023 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Picking Put In Pack Restriction",
    "summary": "Force or disallow the use of destination packages per operation type",
    "version": "20.0.1.0.0",
    "category": "Inventory",
    "author": "Camptocamp, BCIM, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "maintainers": ["TDu"],
    "license": "AGPL-3",
    "depends": ["stock"],
    "data": ["views/stock_picking_type.xml", "views/stock_picking.xml"],
}
