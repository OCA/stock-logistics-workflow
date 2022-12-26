# Copyright 2022 Camptocamp SA (https://www.camptocamp.com).
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Lot Shipment Traceability",
    "summary": "Show the Shipments directly or indirectly involving a Lot/SN",
    "version": "12.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "maintainers": ["ivantodorovich"],
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "license": "AGPL-3",
    "category": "Stock",
    "depends": ["stock_production_lot_traceability"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "reports/stock_shipment_traceability_report.xml",
        "wizards/stock_shipment_traceability_report_wizard.xml",
    ],
}
