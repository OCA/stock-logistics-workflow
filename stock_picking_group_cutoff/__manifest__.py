# Copyright 2020 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock picking group by cut-off date",
    "Summary": """
    When grouping orders and using cut-off dates
    you must group orders by date as well, to not end up w/ tons of orders.
    """,
    "version": "13.0.1.0.0",
    "development_status": "Alpha",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "category": "Warehouse Management",
    "depends": [
        "stock_picking_group_by_partner_by_carrier",
        "stock_picking_group_by_partner_by_carrier_by_date",
        "sale_cutoff_time_delivery",
    ],
    "installable": True,
    "auto_install": True,
    "license": "AGPL-3",
}
