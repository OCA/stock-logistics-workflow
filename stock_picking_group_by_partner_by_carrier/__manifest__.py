# Copyright 2020 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Picking: group by partner and carrier",
    "Summary": "Group sales deliveries moves in 1 picking per partner and carrier",
    "version": "14.0.1.4.2",
    "development_status": "Beta",
    "author": "Camptocamp, BCIM, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "category": "Warehouse Management",
    "depends": [
        "delivery_procurement_group_carrier",
        "stock_move_assign_picking_hook",
    ],
    "data": [
        "views/res_partner.xml",
        "views/stock_picking_type.xml",
        "views/stock_warehouse.xml",
        "report/assets.xml",
        "report/report_delivery_slip.xml",
        "wizard/stock_picking_merge_wiz.xml",
        "wizard/stock_picking_merge_wiz_info_template.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "license": "AGPL-3",
}
