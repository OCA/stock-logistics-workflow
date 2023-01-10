# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Group By Partner By Carrier By Customer",
    "summary": """
        Allows to extend stock_picking_group_by_partner_by_carrier adding a
        grouping per customer""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": [
        "stock_picking_group_by_partner_by_carrier",
        "sale_procurement_customer",
    ],
    "data": [
        "views/stock_picking_type.xml",
    ],
}
