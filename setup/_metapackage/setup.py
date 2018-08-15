import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo10-addons-oca-stock-logistics-workflow",
    description="Meta package for oca-stock-logistics-workflow Odoo addons",
    version=version,
    install_requires=[
        'odoo10-addon-product_expiry_simple',
        'odoo10-addon-product_supplierinfo_for_customer_picking',
        'odoo10-addon-stock_auto_move',
        'odoo10-addon-stock_cancel',
        'odoo10-addon-stock_cancel_delivery',
        'odoo10-addon-stock_delivery_internal',
        'odoo10-addon-stock_disable_force_availability_button',
        'odoo10-addon-stock_lot_scrap',
        'odoo10-addon-stock_move_backdating',
        'odoo10-addon-stock_no_negative',
        'odoo10-addon-stock_ownership_availability_rules',
        'odoo10-addon-stock_ownership_by_move',
        'odoo10-addon-stock_pack_operation_auto_fill',
        'odoo10-addon-stock_picking_backorder_strategy',
        'odoo10-addon-stock_picking_customer_ref',
        'odoo10-addon-stock_picking_filter_lot',
        'odoo10-addon-stock_picking_invoice_link',
        'odoo10-addon-stock_picking_line_sequence',
        'odoo10-addon-stock_picking_mass_action',
        'odoo10-addon-stock_picking_package_preparation',
        'odoo10-addon-stock_picking_package_preparation_line',
        'odoo10-addon-stock_picking_show_backorder',
        'odoo10-addon-stock_picking_show_return',
        'odoo10-addon-stock_picking_transfer_lot_autoassign',
        'odoo10-addon-stock_split_picking',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
