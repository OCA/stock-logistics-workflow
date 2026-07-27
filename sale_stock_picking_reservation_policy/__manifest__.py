# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sale Stock Picking Reservation Policy",
    "summary": "Carry the reservation policy from the sale order to its deliveries.",
    "version": "19.0.1.0.0",
    "category": "Inventory/Configuration",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "license": "AGPL-3",
    "maintainers": ["ivantodorovich"],
    "depends": ["stock_picking_reservation_policy", "sale_stock"],
    "data": [
        "views/res_partner_views.xml",
        "views/sale_order_views.xml",
    ],
    "auto_install": True,
}
