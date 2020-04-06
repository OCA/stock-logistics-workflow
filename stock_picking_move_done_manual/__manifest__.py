# Copyright 2020 ForgeFlow, S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Stock Picking Move Manual Done",
    "summary": "Allow to complete individual moves in a picking.",
    "version": "12.0.1.0.1",
    "author": "ForgeFlow, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "category": "Warehouse Management",
    "depends": [
        "stock_picking_button_validate_hook",
        "stock_move_action_done_hook",
    ],
    "data": [
        'views/stock_picking_views.xml',
    ],
    "license": "LGPL-3",
    'installable': True,
    'application': False,
}
