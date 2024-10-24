# 2024 Copyright ForgeFlow, S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

{
    "name": "Stock Quant Package Restrict Disposable Reuse",
    "version": "16.0.1.0.0",
    "summary": " Prevent the reuse of disposable packages by hiding them from"
    " the package selection list after they have been used in a delivery.",
    "category": "Warehouse Management",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "license": "AGPL-3",
    "depends": ["stock"],
    "data": ["views/stock_package_views.xml", "views/stock_package_type_view.xml"],
    "installable": True,
}
