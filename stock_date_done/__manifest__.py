# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Date Done",
    "summary": "Edit and audit the effective date of stock transfers and scraps",
    "version": "19.0.1.0.0",
    "author": "Quartile, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "category": "Inventory",
    "license": "AGPL-3",
    "depends": ["stock"],
    "data": [
        "security/stock_date_done_security.xml",
        "views/stock_picking_views.xml",
        "views/stock_scrap_views.xml",
    ],
    "pre_init_hook": "pre_init_hook",
    "post_init_hook": "post_init_hook",
    "maintainers": ["yostashiro", "aungkokolin1997"],
    "installable": True,
}
