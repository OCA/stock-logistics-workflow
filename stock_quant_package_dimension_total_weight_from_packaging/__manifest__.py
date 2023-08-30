# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{
    "name": "Stock Quant Package Dimension Total Weight From Packaging",
    "summary": "Estimated weight of a package",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "auto_install": True,
    "depends": [
        "stock_quant_package_dimension",
        # OCA/product-attribute
        "product_total_weight_from_packaging",
    ],
}
