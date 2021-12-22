import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-stock-logistics-workflow",
    description="Meta package for oca-stock-logistics-workflow Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-stock_no_negative>=15.0dev,<15.1dev',
        'odoo-addon-stock_picking_filter_lot>=15.0dev,<15.1dev',
        'odoo-addon-stock_picking_purchase_order_link>=15.0dev,<15.1dev',
        'odoo-addon-stock_picking_show_return>=15.0dev,<15.1dev',
        'odoo-addon-stock_push_delay>=15.0dev,<15.1dev',
        'odoo-addon-stock_restrict_lot>=15.0dev,<15.1dev',
        'odoo-addon-stock_split_picking>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
