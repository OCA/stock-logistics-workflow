import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-stock-logistics-workflow",
    description="Meta package for oca-stock-logistics-workflow Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-purchase_stock_picking_restrict_cancel',
        'odoo12-addon-stock_change_price_at_date',
        'odoo12-addon-stock_landed_costs_currency',
        'odoo12-addon-stock_move_line_auto_fill',
        'odoo12-addon-stock_move_quick_lot',
        'odoo12-addon-stock_no_negative',
        'odoo12-addon-stock_picking_customer_ref',
        'odoo12-addon-stock_picking_filter_lot',
        'odoo12-addon-stock_picking_invoice_link',
        'odoo12-addon-stock_picking_line_sequence',
        'odoo12-addon-stock_picking_mass_action',
        'odoo12-addon-stock_picking_operation_quick_change',
        'odoo12-addon-stock_picking_package_preparation',
        'odoo12-addon-stock_picking_package_preparation_line',
        'odoo12-addon-stock_picking_quick',
        'odoo12-addon-stock_picking_restrict_cancel_with_orig_move',
        'odoo12-addon-stock_picking_sale_order_link',
        'odoo12-addon-stock_picking_send_by_mail',
        'odoo12-addon-stock_picking_show_backorder',
        'odoo12-addon-stock_picking_show_return',
        'odoo12-addon-stock_split_picking',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
