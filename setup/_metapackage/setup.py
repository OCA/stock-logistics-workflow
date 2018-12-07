import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-stock-logistics-workflow",
    description="Meta package for oca-stock-logistics-workflow Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-mrp_stock_picking_restrict_cancel',
        'odoo11-addon-product_expiry_simple',
        'odoo11-addon-purchase_stock_picking_restrict_cancel',
        'odoo11-addon-stock_batch_picking',
        'odoo11-addon-stock_lot_scrap',
        'odoo11-addon-stock_no_negative',
        'odoo11-addon-stock_pack_operation_auto_fill',
        'odoo11-addon-stock_picking_auto_create_lot',
        'odoo11-addon-stock_picking_backorder_strategy',
        'odoo11-addon-stock_picking_customer_ref',
        'odoo11-addon-stock_picking_filter_lot',
        'odoo11-addon-stock_picking_invoice_link',
        'odoo11-addon-stock_picking_mass_action',
        'odoo11-addon-stock_picking_operation_quick_change',
        'odoo11-addon-stock_picking_package_preparation',
        'odoo11-addon-stock_picking_package_preparation_line',
        'odoo11-addon-stock_picking_purchase_propagate',
        'odoo11-addon-stock_picking_restrict_cancel_with_orig_move',
        'odoo11-addon-stock_picking_sale_order_link',
        'odoo11-addon-stock_picking_send_by_mail',
        'odoo11-addon-stock_picking_show_backorder',
        'odoo11-addon-stock_picking_show_return',
        'odoo11-addon-stock_picking_whole_scrap',
        'odoo11-addon-stock_split_picking',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
