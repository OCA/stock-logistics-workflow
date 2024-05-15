# Copyright 2015-2016 Agile Business Group (<http://www.agilebg.com>)
# Copyright 2015 BREMSKERL-REIBBELAGWERKE EMMERLING GmbH & Co. KG
#    Author Marco Dieckhoff
# Copyright 2018 Alex Comba - Agile Business Group
# Copyright 2023 Simone Rubino - TAKOBI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Stock Move Backdating',
    'version': '12.0.1.0.1',
    'category': 'Stock Logistics',
    'license': 'AGPL-3',
    'author': 'Marco Dieckhoff, BREMSKERL, Agile Business Group, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/stock-logistics-workflow'
               '/tree/12.0/stock_move_backdating',
    'depends': [
        'stock_account',
    ],
    'data': [
        'wizards/fill_date_backdating.xml',
        'views/stock_inventory_views.xml',
        'views/stock_picking.xml',
    ],
    'installable': True,
}
