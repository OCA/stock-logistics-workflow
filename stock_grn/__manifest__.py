# Copyright 2015 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Goods Received Note",
    "version": "16.0.1.0.1",
    "author": "BCIM, ACSONE SA/NV, Odoo Community Association (OCA)",
    "category": "Delivery",
    "depends": ["stock"],
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "data": [
        "views/stock_grn_views.xml",
        "views/stock_picking_views.xml",
        "views/stock_picking_type_views.xml",
        "views/stock_move_views.xml",
        "data/stock_grn.xml",
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
    ],
    "installable": True,
    "auto_install": False,
    "license": "AGPL-3",
}
