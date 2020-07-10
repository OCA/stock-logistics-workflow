# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Shipping expedition',
    'version': '12.0.1.0.0',    
    'author': 'Odoo Nodriza Tech (ONT), Odoo Community Association (OCA),',
    'website': 'https://nodrizatech.com/',
    'category': 'Delivery',
    'license': 'AGPL-3',
    'depends': ['base', 'delivery', 'stock', 'cashondelivery', 'stock_picking_sale_order'],
    'data': [
        'data/ir_cron.xml',
        'views/delivery_carrier.xml',
        'views/shipping_expedition.xml',
        'views/res_partner.xml',
        'views/crm_lead.xml',
        'views/sale_order.xml',
        'views/stock_picking.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,    
}