# Copyright 2022 ArcheTI (https://archeti.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Sub State",
    "version": "13.0.1.0.0",
    "category": "Tools",
    "author": "ArcheTI, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "license": "AGPL-3",
    "depends": ["base_substate", "stock"],
    "data": [
        "views/stock_picking_views.xml",
        "data/picking_substate_mail_template_data.xml",
        "data/picking_substate_data.xml",
    ],
    "demo": ["data/picking_substate_demo.xml"],
    "installable": True,
}
