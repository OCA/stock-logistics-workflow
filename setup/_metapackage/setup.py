import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-stock-logistics-workflow",
    description="Meta package for oca-stock-logistics-workflow Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-stock_auto_move',
        'odoo14-addon-stock_delivery_note',
        'odoo14-addon-stock_move_assign_picking_hook',
        'odoo14-addon-stock_move_line_auto_fill',
        'odoo14-addon-stock_no_negative',
        'odoo14-addon-stock_picking_back2draft',
        'odoo14-addon-stock_picking_filter_lot',
        'odoo14-addon-stock_picking_invoice_link',
        'odoo14-addon-stock_picking_line_sequence',
        'odoo14-addon-stock_putaway_hook',
        'odoo14-addon-stock_quant_package_dimension',
        'odoo14-addon-stock_quant_package_product_packaging',
        'odoo14-addon-stock_restrict_lot',
        'odoo14-addon-stock_return_request',
        'odoo14-addon-stock_valuation_layer_by_category',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
