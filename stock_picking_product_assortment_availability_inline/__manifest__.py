# Copyright 2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Stock Picking Product Assortment Availability Inline",
    "summary": "Glue module to display stock available when an assortment is defined "
    "for a partner",
    "version": "15.0.1.0.0",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": ["Sergio-teruel"],
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "stock_picking_product_assortment",
        "stock_picking_product_availability_inline",
    ],
    "data": ["views/stock_picking_view.xml"],
    "auto_install": True,
}
