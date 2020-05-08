# Copyright 2020 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Stock Picking Button Validate Hook",
    "summary": "Add more flexibility in the validation of pickings.",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "version": "12.0.1.0.0",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "license": 'LGPL-3',
    "depends": [
        'stock',
    ],
    "installable": True,
    "post_load": 'post_load_hook',
}
