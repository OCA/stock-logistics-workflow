# Copyright 2012-2014 Alexandre Fayolle, Camptocamp SA
# Copyright 2018 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Stock batch picking',
    'summary': 'Allows manage a lot of pickings in batch',
    'version': '12.0.1.0.1',
    'author': "Camptocamp, "
              "Tecnativa, "
              "Odoo Community Association (OCA)",
    'development_status': 'Mature',
    'maintainers': [
        'Camptocamp',
        'Tecnativa',
    ],
    'category': 'Warehouse Management',
    'depends': [
        'stock_picking_batch',
        'delivery',
        'stock_picking_mass_action',
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
        'views/res_config_settings_views.xml',
        'wizard/batch_picking_creator_view.xml',
    ],
    'installable': True,
    'license': 'AGPL-3',
}
