import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-oca-stock-logistics-workflow",
    description="Meta package for oca-stock-logistics-workflow Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-mrp_lock_lot',
        'odoo8-addon-picking_dispatch',
        'odoo8-addon-procurement_jit_assign_move',
        'odoo8-addon-product_unique_serial',
        'odoo8-addon-sale_stock_auto_move',
        'odoo8-addon-sale_stock_picking_back2draft',
        'odoo8-addon-stock_auto_move',
        'odoo8-addon-stock_disable_force_availability_button',
        'odoo8-addon-stock_dropshipping_dual_invoice',
        'odoo8-addon-stock_lock_lot',
        'odoo8-addon-stock_lot_scrap',
        'odoo8-addon-stock_move_backdating',
        'odoo8-addon-stock_move_description',
        'odoo8-addon-stock_no_negative',
        'odoo8-addon-stock_ownership_availability_rules',
        'odoo8-addon-stock_ownership_by_move',
        'odoo8-addon-stock_picking_back2draft',
        'odoo8-addon-stock_picking_backorder_strategy',
        'odoo8-addon-stock_picking_backorder_to_sale',
        'odoo8-addon-stock_picking_compute_delivery_date',
        'odoo8-addon-stock_picking_deliver_uos',
        'odoo8-addon-stock_picking_invoice_link',
        'odoo8-addon-stock_picking_manual_procurement_group',
        'odoo8-addon-stock_picking_mass_action',
        'odoo8-addon-stock_picking_package_preparation',
        'odoo8-addon-stock_picking_package_preparation_line',
        'odoo8-addon-stock_picking_reorder_lines',
        'odoo8-addon-stock_picking_show_return',
        'odoo8-addon-stock_route_sales_team',
        'odoo8-addon-stock_scanner',
        'odoo8-addon-stock_split_picking',
        'odoo8-addon-stock_transfer_split_multi',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
