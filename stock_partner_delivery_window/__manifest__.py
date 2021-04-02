# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
{
    "name": "Stock Partner Delivery Window",
    "summary": "Define preferred delivery time windows for partners",
    "version": "13.0.1.2.0",
    "category": "Inventory",
    "author": "Camptocamp, ACSONE SA/NV, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["base_time_window", "partner_tz", "stock"],
    "data": ["security/ir.model.access.csv", "views/res_partner.xml"],
    "demo": ["demo/delivery_time_window.xml"],
    "installable": True,
}
