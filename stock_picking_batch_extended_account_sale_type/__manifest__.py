# Copyright 2022 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock batch picking extended account sale type",
    "summary": "Generates invoices when batch is set to Done state",
    "version": "15.0.1.0.0",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "maintainers": ["ernestotejeda"],
    "development_status": "Beta",
    "category": "Warehouse Management",
    "depends": ["stock_picking_batch_extended_account", "sale_order_type"],
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "data": ["views/sale_order_type_views.xml"],
    "installable": True,
    "license": "AGPL-3",
}
