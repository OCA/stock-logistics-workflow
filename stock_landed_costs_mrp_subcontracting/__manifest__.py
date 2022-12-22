# Copyright 2021 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Stock Landed Costs MRP Subcontracting",
    "summary": "When using Subcontracting, use the incoming shipment in "
    "landed costs",
    "version": "14.0.1.1.0",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["mrp_subcontracting_account", "stock_landed_costs"],
    "post_init_hook": "post_init_hook",
}
