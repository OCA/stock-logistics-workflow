# Copyright 2020 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Stock Account Product Run FIFO Hook",
    "summary": "Add more flexibility in the run fifo method.",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "version": "17.0.1.0.1",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "license": "LGPL-3",
    "depends": ["stock_account"],
    "installable": True,
    "post_load": "post_load_hook",
}
