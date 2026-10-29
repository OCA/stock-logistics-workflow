# Copyright 2020 Camptocamp
# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Return Lot",
    "summary": "Propagate SN/lots from origin picking to return picking.",
    "version": "19.0.1.1.0",
    "license": "AGPL-3",
    "author": "Camptocamp, ACSONE SA/NV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["stock_restrict_lot", "stock_picking_return_restricted_qty"],
    "data": [
        "views/res_config_settings_views.xml",
        "wizards/stock_return_picking.xml",
    ],
}
