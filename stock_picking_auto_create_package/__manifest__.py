# Copyright 2023 Raumschmiede Gmbh
# Copyright 2023 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Picking Auto Create Package",
    "summary": """
        Put all move lines in packs on validation.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "BCIM,MT Software,Raumschmiede,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": [
        "stock",
    ],
    "data": [
        "views/stock_picking_type.xml",
    ],
}
