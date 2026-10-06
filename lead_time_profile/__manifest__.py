# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Lead Time Profile",
    "summary": "Manage lead times using rule-based lead time profiles",
    "version": "16.0.1.0.0",
    "author": "Quartile, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "license": "AGPL-3",
    "depends": ["stock"],
    "data": [
        "security/lead_time_profile_security.xml",
        "security/ir.model.access.csv",
        "views/lead_time_profile_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "maintainers": ["yostashiro", "aungkokolin1997"],
    "installable": True,
}
