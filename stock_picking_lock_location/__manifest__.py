# Copyright 2025 Akretion (https://www.akretion.com).
# @author Mathieu Delva <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Lock Location",
    "summary": "Add boolean on location type to lock location on picking",
    "version": "18.0.1.1.0",
    "category": "Stock",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Akretion, Odoo Community Association (OCA)",
    "maintainers": ["mathieudelva"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock",
    ],
    "data": [
        "views/res_config_settings_views.xml",
        "views/stock_picking_type_views.xml",
        "views/stock_picking_views.xml",
    ],
}
