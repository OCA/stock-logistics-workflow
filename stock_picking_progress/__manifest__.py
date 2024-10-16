# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Stock Picking Progress",
    "summary": "Compute the stock.picking progression",
    "version": "14.0.1.2.1",
    "category": "Inventory",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "mmequignon, Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["mmequignon", "JuMiSanAr"],
    "license": "AGPL-3",
    "installable": True,
    "depends": ["stock"],
    "data": ["views/stock_picking.xml"],
    "pre_init_hook": "pre_init_hook",
    "post_init_hook": "post_init_hook",
}
