# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Stock Valuation Fifo Lot Allocation",
    "version": "16.0.1.0.0",
    "category": "Warehouse Management",
    "development_status": "Alpha",
    "license": "AGPL-3",
    "summary": "Keep a per-lot ledger of the inventory value allocated by each "
    "stock valuation layer",
    "author": "Quartile, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["stock_valuation_fifo_lot", "stock_move_actual_date"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "views/stock_valuation_lot_allocation_views.xml",
    ],
    "installable": True,
    "post_init_hook": "post_init_hook",
    "maintainers": ["yostashiro", "AungKoKoLin1997"],
}
