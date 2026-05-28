# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Auto Process",
    "summary": "Automatically confirm, assign and validate stock pickings "
    "based on configurable rules",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "Inventory",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Quartile, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["stock"],
    "data": [
        "security/stock_auto_process_security.xml",
        "security/ir.model.access.csv",
        "security/stock_auto_process_rule.xml",
        "data/ir_cron_data.xml",
        "views/stock_auto_process_rule_views.xml",
    ],
    "installable": True,
    "maintainers": ["yostashiro", "aungkokolin1997"],
}
