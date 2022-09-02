# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Sale Line Returned Qty",
    "summary": "Track returned quantity of sale order lines.",
    "version": "15.0.1.0.0",
    "category": "Sales",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "installable": True,
    "depends": ["sale_stock"],
    "data": ["views/sale_order_views.xml"],
}
