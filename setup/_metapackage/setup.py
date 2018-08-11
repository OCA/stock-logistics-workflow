import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo9-addons-oca-stock-logistics-workflow",
    description="Meta package for oca-stock-logistics-workflow Odoo addons",
    version=version,
    install_requires=[
        'odoo9-addon-stock_account_deposit',
        'odoo9-addon-stock_auto_move',
        'odoo9-addon-stock_batch_picking',
        'odoo9-addon-stock_deposit',
        'odoo9-addon-stock_disable_force_availability_button',
        'odoo9-addon-stock_lot_scrap',
        'odoo9-addon-stock_no_negative',
        'odoo9-addon-stock_pack_operation_auto_fill',
        'odoo9-addon-stock_pack_operation_quick_lot',
        'odoo9-addon-stock_picking_digitized_signature',
        'odoo9-addon-stock_picking_invoice_link',
        'odoo9-addon-stock_picking_line_sequence',
        'odoo9-addon-stock_picking_mass_assign',
        'odoo9-addon-stock_picking_operation_quick_change',
        'odoo9-addon-stock_picking_package_preparation',
        'odoo9-addon-stock_picking_package_preparation_line',
        'odoo9-addon-stock_picking_sale_order_link',
        'odoo9-addon-stock_picking_send_by_mail',
        'odoo9-addon-stock_picking_show_backorder',
        'odoo9-addon-stock_picking_show_return',
        'odoo9-addon-stock_picking_tracking',
        'odoo9-addon-stock_picking_transfer_lot_autoassign',
        'odoo9-addon-stock_scrap',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
