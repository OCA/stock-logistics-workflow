# Copyright 2023 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Picking Put In Pack Restriction",
    "summary": """
        Adds a restriction on transfer type to force or disallow
        the use of destination package.
    """,
    "version": "14.0.1.0.0",
    "category": "Inventory",
    "author": "Camptocamp, BCIM, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "maintainsers": ["TDu"],
    "license": "AGPL-3",
    "depends": ["stock"],
    "application": False,
    "installable": True,
    "data": ["views/stock_picking_type.xml", "views/stock_picking.xml"],
}
