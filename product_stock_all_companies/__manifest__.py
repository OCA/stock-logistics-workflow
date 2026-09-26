# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Product Stock All Companies",
    "summary": """
        Show the stock of a product in all the warehouses,
        even if they are from other companies.
        If the product has more than one variant,
        the stock will only be shown in the variants of the product.
    """,
    "author": "Solvos, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "version": "18.0.1.0.0",
    "category": "Inventory/Inventory",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/product_views.xml",
        "views/product_template_views.xml",
    ],
    "installable": True,
}
