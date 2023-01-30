# Copyright 2023 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Internal Resupply Stock In",
    "summary": "Automatic pickings for Internal Resupply",
    "version": "14.0.1.0.0",
    "category": "Logistic",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Akretion, Odoo Community Association (OCA)",
    "maintainers": ["Kev-Roche"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "stock_reception_dedicate_picking_type",
    ],
    "data": [
        "views/stock_picking.xml",
    ],
}
