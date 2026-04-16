# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Stock Picking - Partner/Customer VAT",
    "summary": """
        This module extends the picking functionality. It allows:
        * Displaying the partner's VAT on the picking form view.
        * Displaying the partner's VAT on reports:
            * Picking Operations
            * Delivery Slip
    """,
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Solvos," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "depends": ["stock"],
    "data": ["views/report_delivery_document.xml", "views/stock_picking_views.xml"],
}
