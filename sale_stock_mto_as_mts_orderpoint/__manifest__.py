# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Sale Stock Mto As Mts Orderpoint",
    "summary": "Materialize need from MTO route through orderpoint",
    "version": "14.0.1.0.1",
    "development_status": "Alpha",
    "category": "Operations/Inventory/Delivery",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale_stock", "stock_orderpoint_manual_procurement"],
    "data": [
        "data/stock_data.xml",
    ],
}
