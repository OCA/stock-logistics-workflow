# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Quant Lock",
    "summary": "Lock selected quants to prevent new reservations "
    "and keep stock move traceability",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV, BCIM, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": [
        "stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_picking_type_views.xml",
        "views/stock_quant_views.xml",
        "wizards/stock_quant_lock_wizard_views.xml",
    ],
    "maintainers": ["lmignon", "jbaudoux"],
    "installable": True,
}
