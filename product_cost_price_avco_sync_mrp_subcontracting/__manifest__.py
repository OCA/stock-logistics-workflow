# Copyright 2023 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Product cost price avco sync for mrp subcontracts",
    "summary": "Set product cost price from updated moves that implies productions",
    "version": "13.0.1.0.1",
    "development_status": "Production/Stable",
    "category": "Stock",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["product_cost_price_avco_sync_mrp", "mrp_subcontracting_account"],
    "pre_init_hook": "pre_init_hook",
}
