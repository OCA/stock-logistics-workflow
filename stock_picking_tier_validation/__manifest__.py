# Copyright Sistemas de Datos
# Copyright 2020 Quartile Limited
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Picking Tier Validation",
    "summary": "Extends the functionality of Pickings to "
    "support a tier validation process.",
    "version": "12.0.1.0.0",
    "category": "Warehouse Management",
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "author": "Sistemas de Datos, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["stock", "base_tier_validation"],
    "data": ["views/stock_picking_views.xml"],
    "application": False,
    "installable": True,
}
