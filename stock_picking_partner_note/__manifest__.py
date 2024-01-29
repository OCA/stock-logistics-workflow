# Copyright 2024 Camptocamp (<https://www.camptocamp.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Picking Partner Note",
    "version": "16.0.1.0.0",
    "development_status": "Beta",
    "category": "Product",
    "summary": "Add partner notes on picking",
    "author": "Camptocamp, BCIM, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "license": "AGPL-3",
    "depends": ["sale_stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner.xml",
        "views/stock_picking_note_type.xml",
        "views/stock_picking_type.xml",
        "views/stock_picking_note.xml",
        "views/stock_picking_partner_note_menus.xml",
    ],
    "installable": True,
    "auto_install": False,
}
