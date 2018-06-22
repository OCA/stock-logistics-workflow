# Copyright 2012-2014 Alexandre Fayolle, Camptocamp SA
# Copyright 2018 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Stock batch picking',
    'summary': 'Allows manage a lot of pickings in batch',
    'version': '11.0.1.0.0',
    'author': "Camptocamp, "
              "Tecnativa, "
              "Odoo Community Association (OCA)",
    'maintainers': [
        'Camptocamp',
        'Tecnativa',
    ],
    'category': 'Inventory',
    'depends': [
        'delivery',
    ],
    'website': 'https://github.com/OCA/stock-logistics-workflow',
    'data': [
        'data/stock_batch_picking_sequence.xml',
        'data/batch_picking_actions_server.xml',
        'views/stock_batch_picking.xml',
        'views/product_product.xml',
        'views/report_batch_picking.xml',
        'views/stock_picking.xml',
        'views/stock_warehouse.xml',
        'wizard/batch_picking_creator_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'license': 'AGPL-3',
}
