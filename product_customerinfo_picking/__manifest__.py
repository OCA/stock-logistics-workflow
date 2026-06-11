# Copyright 2013 - 2021 Agile Business Group sagl (<https://www.agilebg.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Product Customerinfo Picking",
    "version": "19.0.1.0.0",
    "author": "Agile Business Group, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "category": "Stock",
    "summary": "This module makes the product customer code visible "
    "in the stock moves of a picking.",
    "license": "AGPL-3",
    "depends": ["stock", "product_customerinfo"],
    "data": [
        "views/res_config_settings_view.xml",
        "views/stock_picking_view.xml",
        "reports/report_delivery_document_template.xml",
        "reports/report_picking_template.xml",
    ],
    "installable": True,
}
