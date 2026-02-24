# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Stock Picking Auto-Pack Control",
    "version": "19.0.1.0.0",
    "category": "Logistic",
    "license": "AGPL-3",
    "summary": "Prevents the automatic creation of individual packages "
    "for products without defined packaging rules.",
    "author": "ForgeFlow S.L., Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["stock_picking_auto_create_package"],
    "data": [
        "views/stock_picking_type_views.xml",
    ],
    "installable": True,
}
