# -*- coding: utf-8 -*-
{
    'name': "Product Serial Unique Number",
    'author': "vauxoo",
    'website': "http://www.vauxoo.com",
    'category': 'stock',
    'version': '1.0',
    'depends': ['stock_no_negative'],
    'data': [
        "views/product_view.xml",
        "views/stock_view.xml",
    ],
    'demo': [
        "demo/test_demo.xml",
    ],
    'installable': True,
    'auto_install': False,
}
