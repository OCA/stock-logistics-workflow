# Copyright (C) 2026 Binhex
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Move Line Portal",
    "summary": "Show customer stock movements (incoming/outgoing) in portal",
    "version": "17.0.1.0.0",
    "depends": ["portal", "stock"],
    "author": "Binhex, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "data": [
        "security/ir.model.access.csv",
        "views/stock_move_line_template.xml",
    ],
    "demo": ["data/demo.xml"],
    "installable": True,
}
