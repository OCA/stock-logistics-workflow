# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Sale Stock MTO as MTS Orderpoint Product Variant",
    "version": "14.0.1.0.0",
    "development_status": "Alpha",
    "category": "Operations/Inventory/Delivery",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["mmequignon"],
    "license": "AGPL-3",
    "installable": True,
    "auto_install": True,
    "depends": [
        "sale_stock_mto_as_mts_orderpoint",
        "stock_product_variant_mto",
    ],
}
