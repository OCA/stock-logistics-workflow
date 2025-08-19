# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Split Picking Dimension",
    "summary": """Split a picking in two not transferred pickings to ensure that the """
    """first one doesn't exceed given dimensions (nbr lines, volume, weight)""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": [
        "stock_picking_volume",  # OCA/stock-logistics-warehouse
        "stock_split_picking",  # OCA/stock-logistics-worflow
    ],
    "data": [
        "wizards/stock_split_picking.xml",
    ],
    "demo": [],
}
