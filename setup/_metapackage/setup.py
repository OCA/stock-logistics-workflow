import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-stock-logistics-workflow",
    description="Meta package for oca-stock-logistics-workflow Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-stock_no_negative',
        'odoo14-addon-stock_picking_invoice_link',
        'odoo14-addon-stock_putaway_hook',
        'odoo14-addon-stock_restrict_lot',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
