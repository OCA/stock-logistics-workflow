# Copyright 2021 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Shifting End of lot",
    "summary": "Move product lot quantity rest to another location",
    "version": "12.0.1.0.2",
    "author": "Akretion, Odoo Community Association (OCA)",
    "category": "Stock",
    "depends": [
        "stock",
    ],
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "data": [
        "views/picking_type.xml",
    ],
    "demo": [
        "data/organisation_demo.xml",
        "data/product_demo.xml",
        "data/stock_demo.xml",
    ],
    "development_status": "Alpha",
    "maintainers": ["bealdav"],
    "installable": True,
    "license": "AGPL-3",
}
