# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Scrap Reason Mandatory",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "summary": "Make the reason required on Scrap Order form view",
    "author": "Trobz, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "category": "Warehouse Management",
    "depends": ["stock"],
    "data": [
        "views/stock_scrap_views.xml",
        "views/stock_config_settings_views.xml",
    ],
    "installable": True,
}
