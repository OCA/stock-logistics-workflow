# Copyright 2014 NDP Systèmes (<https://www.ndp-systemes.fr>)
# Copyright 2020 ACSONE SA/NV (<https://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Automatic Move Processing",
    "version": "13.0.1.0.0",
    "author": "NDP Systèmes, ACSONE SA/NV, Odoo Community Association (OCA)",
    "category": "Warehouse",
    "development_status": "Production/Stable",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["stock"],
    "data": [
        "data/procurement_group.xml",
        "views/stock_move.xml",
        "views/stock_rule.xml",
    ],
    "demo": [
        "demo/stock_location.xml",
        "demo/stock_location_route.xml",
        "demo/stock_rule.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
