# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Restrict Lot Domain",
    "summary": "Only apply lot restriction on products in a domain",
    "version": "14.0.1.0.0",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Ooops404, PyTech SRL, Odoo Community Association (OCA)",
    "maintainers": ["aleuffre", "renda-dev"],
    "license": "AGPL-3",
    "installable": True,
    "depends": ["stock_restrict_lot"],
    "data": [
        "views/stock_picking_views.xml",
        "views/res_config_settings_views.xml",
    ],
}
