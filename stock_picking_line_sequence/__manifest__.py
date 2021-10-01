# Copyright 2017 Camptocamp SA - Damien Crier, Alexandre Fayolle
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock picking lines with sequence number",
    "summary": "Manages the order of stock moves by displaying its sequence",
    "version": "13.0.1.0.0",
    "category": "Warehouse Management",
    "author": "Camptocamp, "
    "Eficent, "
    "Serpent CS, "
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["stock", "sale", "sale_stock"],
    "data": ["views/stock_view.xml", "report/report_deliveryslip.xml"],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "auto_install": False,
    "license": "AGPL-3",
}
