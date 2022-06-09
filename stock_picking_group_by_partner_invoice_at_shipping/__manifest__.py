# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Picking Group By Partner Monthly Invoice",
    "summary": "Glue module between the picking grouping and monthly invoicing",
    "version": "14.0.1.0.0",
    "development_status": "Alpha",
    "category": "Warehouse Management",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "stock_picking_group_by_partner_by_carrier",
        "account_invoice_mode_at_shipping",
    ],
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "installable": True,
    "auto_install": True,
}
