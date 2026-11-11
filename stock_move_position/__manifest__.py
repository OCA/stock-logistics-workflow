# Copyright 2026 Camptocamp SA
# @author Akim Juillerat <akim.juillerat@camptocamp.com>
# @author Ricardo Almeida Soares <ricardo.almeidasoares@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Stock Move Position",
    "summary": "Adds position to stock move and numbering from picking",
    "version": "19.0.1.1.0",
    "category": "stock",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "license": "AGPL-3",
    "depends": [
        # OCA/server-ux
        "base_line_numbering",
        # Odoo
        "stock_picking_batch",
    ],
    "data": [
        "views/stock_picking_batch.xml",
        "views/stock_picking.xml",
    ],
}
