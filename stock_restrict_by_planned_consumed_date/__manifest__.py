# Copyright 2024 Foodles (https://www.foodles.co)
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock restrict by planned consumed date",
    "Summary": "Do not reserved stock if expiration time is before planned consumed date.",
    "version": "14.0.1.0.0",
    "development_status": "Beta",
    "author": "Pierre Verkest <pierreverkest84@gmail.com>, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "category": "Warehouse Management",
    "depends": [
        "stock_move_planned_consumed_date",
        "product_expiry",
    ],
    "installable": True,
    "license": "AGPL-3",
}
