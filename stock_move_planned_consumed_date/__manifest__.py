# Copyright 2024 Foodles (https://www.foodles.co)
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Move planned consumed date",
    "Summary": "Do not merge stock move with different planned consumed date.",
    "version": "14.0.0.1.0",
    "development_status": "Beta",
    "author": "Pierre Verkest <pierreverkest84@gmail.com>, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "category": "Warehouse Management",
    "depends": ["stock"],
    "installable": True,
    "license": "AGPL-3",
    "data": [
        "views/stock_picking_views.xml",
    ],
}
