# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Group By Max Weight",
    "summary": """
        Allows to filter available pickings for which a maximum weight is not exceeded.""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": [
        "stock_picking_group_by_base",
        "delivery",
    ],
    "data": ["views/stock_picking_type.xml"],
    "pre_init_hook": "pre_init_hook",
}
