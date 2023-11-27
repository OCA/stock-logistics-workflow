# Copyright 2023 Foodles (https://www.foodles.com/)
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Picking Return Restrict Lot",
    "summary": """This module prepare global returns restricting lots on returns picking.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "development_status": "Alpha",
    "author": "Pierre Verkest <pierreverkest84@gmail.com, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": [
        "stock",
        "stock_restrict_lot",
    ],
    "data": [
        "views/stock_picking.xml",
    ],
    "maintainers": ["petrus-v"],
}
