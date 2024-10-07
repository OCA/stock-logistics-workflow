# Copyright 2024 Foodles (https://www.foodles.co)
# @author Alexandre Galdeano <alexandre.galdeano@foodles.co>
# @author Damien Crier <damien.crier@foodles.co>
# @author Pierre Verkest <pierreverkest84@gmail.com>
# @author Matthias Barkat <matthias.barkat@foodles.co>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Rule Delays in Workable Days",
    "summary": """
    TODO
    """,
    "version": "14.0.0.1.0",
    "author": "Alexandre Galdeano <alexandre.galdeano@foodles.co>, "
    "Damien Crier <damien.crier@foodles.co>, "
    "Pierre Verkest <pierreverkest84@gmail.com>, "
    "Matthias Barkat <matthias.barkat@foodles.co>, "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "license": "AGPL-3",
    "installable": True,
    "development_status": "Alpha",
    "depends": [
        "calendar",
        "product_expiry",
        "sale_purchase_stock",
        "stock_location_warehouse",
        "stock",
        "resource",
        "stock_restrict_by_planned_consumed_date",
        "stock_move_planned_consumed_date",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/weekdays.xml",
        "views/res_partner_views.xml",
        "views/stock_rule_views.xml",
        "views/stock_warehouse_views.xml",
        "views/weekday_views.xml",
    ],
    "demo": [
        "demo/lead_times_by_day_demo.xml",
        "demo/product_demo.xml",
        "demo/stock_route_demo.xml",
    ],
}
