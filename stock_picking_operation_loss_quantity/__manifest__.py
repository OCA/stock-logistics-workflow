# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2018 Okia SPRL <sylvain@okia.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Operation Loss Quantity",
    "summary": """
        Declare loss product quantities during picking operations, locking the
        missing stock so it cannot be reserved elsewhere""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV, Okia, BCIM, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": [
        "stock",
        "stock_quant_lock",
    ],
    "data": [
        "views/stock_move_line.xml",
        "views/stock_warehouse.xml",
    ],
}
