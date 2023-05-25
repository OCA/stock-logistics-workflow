# Copyright 2023 Raumschmiede (http://www.raumschmiede.de)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Location Package Restriction",
    "summary": """
        Prevent to mix different packages on the same stock location""",
    "version": "14.0.1.0.0",
    "category": "Warehouse Management",
    "author": "Raumschmiede.de, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "license": "AGPL-3",
    "depends": ["stock"],
    "application": False,
    "installable": True,
    "data": ["views/stock_location.xml"],
}
