# Copyright 2026 Camptocamp SA
# @author Akim Juillerat <akim.juillerat@camptocamp.com>
# @author Ricardo Almeida Soares <ricardo.almeidasoares@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Stock Picking Batch Move Position",
    "summary": "Adds the position of stock moves in their batch transfer",
    "version": "19.0.1.0.0",
    "category": "stock",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "license": "AGPL-3",
    "depends": [
        # OCA/stock-logistics-workflow
        "stock_move_position",
        # Odoo
        "stock_picking_batch",
    ],
    "data": [
        "views/stock_picking_batch.xml",
    ],
}
