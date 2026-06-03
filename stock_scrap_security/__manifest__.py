# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Scrap Security",
    "summary": """
        Manage stock scrap access rights with dedicated security groups.
    """,
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Solvos," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["stock"],
    "data": [
        "security/stock_scrap_security.xml",
        "security/ir.model.access.csv",
        "views/stock_picking_views.xml",
    ],
}
