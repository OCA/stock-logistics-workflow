# -*- coding: utf-8 -*-
# © 2011-2015 Sylvain Garancher <sylvain.garancher@syleam.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Stock Scanner',
    'summary': 'Allows managing barcode readers with simple scenarios',
    'version': '8.0.1.0.0',
    'category': 'Generic Modules/Inventory Control',
    'website': 'https://odoo-community.org/',
    'author': 'SYLEAM,'
              'ACSONE SA/NV,'
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'application': True,
    'installable': True,
    'depends': [
        'product',
        'stock',
    ],
    'data': [
        'security/stock_scanner_security.xml',
        'security/ir.model.access.csv',
        'data/stock_scanner.xml',
        'data/ir_cron.xml',
        'data/scenarios/Login/Login.scenario',
        'data/scenarios/Logout/Logout.scenario',
        'wizard/stock_scanner_config_wizard_view.xml',
        'views/menu.xml',
        'views/scanner_scenario.xml',
        'views/scanner_scenario_step.xml',
        'views/scanner_scenario_transition.xml',
        'views/scanner_scenario_custom.xml',
        'views/scanner_hardware.xml',
    ],
    'demo': [
        'demo/stock_scanner_demo.xml',
        'demo/Tutorial/Tutorial.scenario',
        'demo/Tutorial/Step_types/Step_types.scenario',
        'demo/Tutorial/Sentinel/Sentinel.scenario',
        'demo/Tests/Tests.scenario',
        'demo/Tests/Barcode/Barcode.scenario',
        'demo/Stock/Stock.scenario',
        'demo/Stock/Inventory/Inventory.scenario',
        'demo/Stock/Location_informations/Location_informations.scenario',
    ],
}
