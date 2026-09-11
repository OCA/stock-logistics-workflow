# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Valuation Layer Removal Date",
    "summary": "Store the removal date of the lots on stock valuation layers.",
    "version": "18.0.1.0.0",
    "author": "Quartile, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "category": "Inventory",
    "license": "AGPL-3",
    "development_status": "Beta",
    "depends": ["product_expiry", "stock_account"],
    "data": ["views/stock_valuation_layer_views.xml"],
    "pre_init_hook": "pre_init_hook",
    "maintainers": ["nobuQuartile", "Aungkokolin1997"],
    "installable": True,
}
