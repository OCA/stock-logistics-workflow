[![Runbot Status](https://runbot.odoo-community.org/runbot/badge/flat/154/8.0.svg)](https://runbot.odoo-community.org/runbot/repo/github-com-oca-server-tools-154)
[![Build Status](https://travis-ci.org/OCA/stock-logistics-workflow.svg?branch=8.0)](https://travis-ci.org/OCA/stock-logistics-workflow)
[![Coverage Status](https://img.shields.io/coveralls/OCA/stock-logistics-workflow.svg)](https://coveralls.io/r/OCA/stock-logistics-workflow?branch=8.0)

Odoo Stock Logistic Workflow
===========================

This project aims to deal with modules related to manage logistic flows. You'll find modules that:

 - Bring support for picking dispatch
 - Hold picking (adding a step in their workflow)
 - Ease the flow creation for the stock_location official module
 - Add filter to manage packing and deliveries

Please don't hesitate to suggest one of your module to this project. Also, you may want to have a look on those other projects here:

 - https://github.com/OCA/stock-logistics-tracking
 - https://github.com/OCA/stock-logistics-barcode
 - https://github.com/OCA/stock-logistics-warehouse

[//]: # (addons)
Available addons
----------------
addon | version | summary
--- | --- | ---
[mrp_lock_lot](mrp_lock_lot/) | 8.0.2.0.0 | MRP Lock Lot
[picking_dispatch](picking_dispatch/) | 8.0.1.2.3 | Picking dispatch
[procurement_jit_assign_move](procurement_jit_assign_move/) | 8.0.1.0.0 | Change the behavior of procurement_jit to assign stock moves
[product_unique_serial](product_unique_serial/) | 8.0.1.0.1 | Product Serial Unique Number
[sale_stock_picking_back2draft](sale_stock_picking_back2draft/) | 8.0.1.0.0 | Pickings back to draft - Sale integration
[stock_auto_move](stock_auto_move/) | 8.0.1.0.0 | Automatic Move Processing
[stock_disable_force_availability_button](stock_disable_force_availability_button/) | 8.0.1.0.0 | Disable force availability button
[stock_dropshipping_dual_invoice](stock_dropshipping_dual_invoice/) | 8.0.0.1.0 | Create both Supplier and Customer Invoices from a Dropshipping Delivery
[stock_lock_lot](stock_lock_lot/) | 8.0.1.1.0 | Stock Lock Lot
[stock_lot_scrap](stock_lot_scrap/) | 8.0.1.0.0 | This module adds a button in Production Lot/Serial Number view form to Scrap all products contained.
[stock_move_description](stock_move_description/) | 8.0.1.0.0 | Stock move description
[stock_no_negative](stock_no_negative/) | 8.0.1.0.1 | Stock Check No Negative
[stock_ownership_availability_rules](stock_ownership_availability_rules/) | 8.0.0.2.0 | Enforce ownership on stock availability
[stock_ownership_by_move](stock_ownership_by_move/) | 8.0.0.1.0 | Preserve Ownership of moves (not pickings) on reception.
[stock_picking_back2draft](stock_picking_back2draft/) | 8.0.1.0.0 | Reopen cancelled pickings
[stock_picking_backorder_strategy](stock_picking_backorder_strategy/) | 8.0.0.1.0 | Picking backordering strategies
[stock_picking_compute_delivery_date](stock_picking_compute_delivery_date/) | 8.0.1.1.0 | Stock Picking Compute Delivery Date
[stock_picking_deliver_uos](stock_picking_deliver_uos/) | 8.0.1.0.0 | Adds fields uos and uos_quantity to Stock Transfer Details
[stock_picking_invoice_link](stock_picking_invoice_link/) | 8.0.2.0.0 | Adds link between pickings and generated invoices
[stock_picking_package_preparation](stock_picking_package_preparation/) | 8.0.1.0.0 | Stock Picking Package Preparation
[stock_picking_package_preparation_line](stock_picking_package_preparation_line/) | 8.0.1.0.0 | Stock Picking Package Preparation Line
[stock_picking_reorder_lines](stock_picking_reorder_lines/) | 8.0.0.1.0 | Provide a new field on stock moves, allowing to manage the orders of moves in a picking.
[stock_picking_show_return](stock_picking_show_return/) | 8.0.1.0.0 | Show returns on stock pickings
[stock_scanner](stock_scanner/) | 8.0.1.0.0 | Allows managing barcode readers with simple scenarios
[stock_split_picking](stock_split_picking/) | 8.0.1.0.0 | Split a picking in two unconfirmed pickings
[stock_transfer_split_multi](stock_transfer_split_multi/) | 8.0.1.0.0 | In the stock transfer wizard, you can split by multiple units

Unported addons
---------------
addon | version | summary
--- | --- | ---
[picking_dispatch_wave](picking_dispatch_wave/) | 0.1 (unported) | Picking Dispatch Wave
[product_customer_code_picking](product_customer_code_picking/) | 1.0 (unported) | Product Customer code for stock picking
[product_serial](product_serial/) | 1.0 (unported) | Enhance Serial Number management
[stock_cancel](stock_cancel/) | 1.2 (unported) | Stock Cancel
[stock_filter_none_zero_qty](stock_filter_none_zero_qty/) | 1.0 (unported) | Filter products in stock
[stock_inventory_retry_assign](stock_inventory_retry_assign/) | 1.0 (unported) | Check Availability after Inventories
[stock_location_flow_creator](stock_location_flow_creator/) | 1.0 (unported) | Create configuration of stock location flow
[stock_move_backdating](stock_move_backdating/) | 1.0 (unported) | Allows back-dating of stock moves
[stock_move_on_hold](stock_move_on_hold/) | 1.0 (unported) | Stock On Hold Status
[stock_obsolete](stock_obsolete/) | 1.0 (unported) | Add product depreciation
[stock_picking_mass_assign](stock_picking_mass_assign/) | 0.2 (unported) | Delivery Orders Mass Assign
[stock_picking_priority](stock_picking_priority/) | 0.2 (unported) | Picking Priority
[stock_sale_filters](stock_sale_filters/) | 1.3 (unported) | SO related filters on stock.picking and sale.order

[//]: # (end addons)

Translation status
------------------

[![Transifex Status](https://www.transifex.com/projects/p/OCA-stock-logistics-workflow-8-0/chart/image_png)](https://www.transifex.com/projects/p/OCA-stock-logistics-workflow-8-0)
