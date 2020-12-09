# Copyright 2020 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Picking: group by partner and carrier and scheduled date",
    "Summary": """Delivery orders will be matched by date too.
    """,
    "version": "13.0.1.1.0",
    "development_status": "Alpha",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "category": "Warehouse Management",
    # TODO: consider splitting the hook for `_assign_picking` defined in
    # `stock_picking_group_by_partner_by_carrier`
    # to avoid depending on `stock_picking_group_by_partner_by_carrier`.
    "depends": ["stock_picking_group_by_partner_by_carrier"],
    "data": ["views/stock_picking_type.xml"],
    "installable": True,
    "license": "AGPL-3",
}
