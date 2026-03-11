{
    "name": "Stock Move Line Devaluation Report",
    "summary": "Report for stock withdrawal valuation with pricelist pricing",
    "version": "16.0.1.0.0",
    "category": "Inventory/Inventory",
    "author": "PopSolutions, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "license": "AGPL-3",
    "depends": ["stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_move_line_devaluation_wizard_views.xml",
        "views/stock_move_line_devaluation_report_views.xml",
        "views/stock_move_line_devaluation_report_template.xml",
    ],
    "installable": True,
    "application": False,
}
