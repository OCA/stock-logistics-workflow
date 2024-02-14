# Copyright 2023, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Stock Picking Difference Warning",
    "version": "15.0.1.0.0",
    "summary": "Raise a warning when the quantity of a product in a picking is "
    "different from the quantity in the stock move.",
    "author": "Jarsa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "license": "LGPL-3",
    "category": "Logistics",
    "depends": ["stock"],
    "data": [
        "wizards/picking_difference_warning_wizard_views.xml",
        "security/ir.model.access.csv",
    ],
}
