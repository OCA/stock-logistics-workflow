# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Stock Picking Type Force Shipping Policy - Group By Partner and Carrier",
    "summary": "Glue module for Picking Type Force Shipping Policy"
    " and Group Transfers by Partner and Carrier",
    "version": "18.0.1.0.0",
    "category": "Hidden",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "auto_install": True,
    "depends": [
        "stock_picking_type_force_move_type",
        # in stock-logistics-workflow
        "stock_picking_group_by_partner_by_carrier",
    ],
    "data": [],
}
