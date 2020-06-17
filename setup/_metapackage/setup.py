import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-stock-logistics-workflow",
    description="Meta package for oca-stock-logistics-workflow Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-stock_lock_lot',
        'odoo13-addon-stock_move_line_auto_fill',
        'odoo13-addon-stock_no_negative',
        'odoo13-addon-stock_picking_auto_create_lot',
        'odoo13-addon-stock_picking_back2draft',
        'odoo13-addon-stock_picking_filter_lot',
        'odoo13-addon-stock_picking_group_by_partner_by_carrier',
        'odoo13-addon-stock_picking_mass_action',
        'odoo13-addon-stock_picking_return_restricted_qty',
        'odoo13-addon-stock_picking_sale_order_link',
        'odoo13-addon-stock_picking_show_return',
        'odoo13-addon-stock_picking_whole_scrap',
        'odoo13-addon-stock_quant_package_dimension',
        'odoo13-addon-stock_quant_package_product_packaging',
        'odoo13-addon-stock_split_picking',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
