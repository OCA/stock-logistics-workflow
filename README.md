[![Build Status](https://travis-ci.org/OCA/stock-logistics-workflow.svg?branch=9.0)](https://travis-ci.org/OCA/stock-logistics-workflow)
[![Coverage Status](https://img.shields.io/coveralls/OCA/stock-logistics-workflow.svg)](https://coveralls.io/r/OCA/stock-logistics-workflow?branch=9.0)

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
[stock_account_deposit](stock_account_deposit/) | 9.0.1.0.0 | Create invoices from deposit locations
[stock_auto_move](stock_auto_move/) | 9.0.1.0.0 | Automatic Move Processing
[stock_batch_picking](stock_batch_picking/) | 9.0.1.0.0 | Stock batch picking
[stock_deposit](stock_deposit/) | 9.0.1.0.1 | Manage deposit locations in your warehouses
[stock_disable_force_availability_button](stock_disable_force_availability_button/) | 9.0.1.0.0 | Disable force availability button
[stock_lot_scrap](stock_lot_scrap/) | 9.0.1.0.0 | This module adds a button in Production Lot/Serial Number view form to Scrap all products contained.
[stock_no_negative](stock_no_negative/) | 9.0.1.0.1 | Disallow negative stock levels by default
[stock_pack_operation_auto_fill](stock_pack_operation_auto_fill/) | 9.0.1.0.0 | Stock pack operation auto fill
[stock_picking_digitized_signature](stock_picking_digitized_signature/) | 9.0.1.0.0 | Stock Picking Digitized Signature
[stock_picking_invoice_link](stock_picking_invoice_link/) | 9.0.2.1.0 | Adds link between pickings and invoices
[stock_picking_line_sequence](stock_picking_line_sequence/) | 9.0.1.0.0 | Stock picking lines with sequence number
[stock_picking_mass_assign](stock_picking_mass_assign/) | 9.0.1.0.0 | Delivery Orders Mass Assign
[stock_picking_operation_quick_change](stock_picking_operation_quick_change/) | 9.0.1.0.0 | Change location of all picking operations
[stock_picking_package_preparation](stock_picking_package_preparation/) | 9.0.1.0.0 | Stock Picking Package Preparation
[stock_picking_package_preparation_line](stock_picking_package_preparation_line/) | 9.0.1.0.0 | Stock Picking Package Preparation Line
[stock_picking_sale_order_link](stock_picking_sale_order_link/) | 9.0.1.0.0 | Link between picking and sale order
[stock_picking_send_by_mail](stock_picking_send_by_mail/) | 9.0.1.0.0 | Send stock picking by email
[stock_picking_show_backorder](stock_picking_show_backorder/) | 9.0.1.0.0 | Provides a new field on stock pickings, allowing to display the corresponding backorders.
[stock_picking_show_return](stock_picking_show_return/) | 9.0.1.0.0 | Show returns on stock pickings
[stock_picking_tracking](stock_picking_tracking/) | 9.0.1.0.0 | Adds a concept of event tracking for stock pickings
[stock_picking_transfer_lot_autoassign](stock_picking_transfer_lot_autoassign/) | 9.0.1.1.0 | Auto-assignation of lots on pickings
[stock_scrap](stock_scrap/) | 9.0.1.0.0 | Adds the ability to scrap products easily.


Unported addons
---------------
addon | version | summary
--- | --- | ---
[picking_dispatch_wave](picking_dispatch_wave/) | 0.1 (unported) | Picking Dispatch Wave
[product_customer_code_picking](product_customer_code_picking/) | 1.0 (unported) | Product Customer code for stock picking
[product_serial](product_serial/) | 1.0 (unported) | Enhance Serial Number management
[stock_cancel](stock_cancel/) | 1.2 (unported) | Stock Cancel
[stock_dropshipping_dual_invoice](stock_dropshipping_dual_invoice/) | 8.0.0.1.0 (unported) | Create both Supplier and Customer Invoices from a Dropshipping Delivery
[stock_inventory_retry_assign](stock_inventory_retry_assign/) | 1.0 (unported) | Check Availability after Inventories
[stock_location_flow_creator](stock_location_flow_creator/) | 1.0 (unported) | Create configuration of stock location flow
[stock_move_backdating](stock_move_backdating/) | 1.0 (unported) | Allows back-dating of stock moves
[stock_move_description](stock_move_description/) | 8.0.1.0.0 (unported) | Stock move description
[stock_move_on_hold](stock_move_on_hold/) | 1.0 (unported) | Stock On Hold Status
[stock_obsolete](stock_obsolete/) | 1.0 (unported) | Add product depreciation
[stock_ownership_availability_rules](stock_ownership_availability_rules/) | 8.0.0.2.0 (unported) | Enforce ownership on stock availability
[stock_ownership_by_move](stock_ownership_by_move/) | 8.0.0.1.0 (unported) | Preserve Ownership of moves (not pickings) on reception.
[stock_picking_backorder_strategy](stock_picking_backorder_strategy/) | 8.0.0.1.0 (unported) | Picking backordering strategies
[stock_picking_compute_delivery_date](stock_picking_compute_delivery_date/) | 8.0.1.1.0 (unported) | Stock Picking Compute Delivery Date
[stock_picking_deliver_uos](stock_picking_deliver_uos/) | 8.0.1.0.0 (unported) | Adds fields uos and uos_quantity to Stock Transfer Details
[stock_picking_priority](stock_picking_priority/) | 0.2 (unported) | Picking Priority
[stock_sale_filters](stock_sale_filters/) | 1.3 (unported) | SO related filters on stock.picking and sale.order
[stock_split_picking](stock_split_picking/) | 8.0.1.0.0 (unported) | Split a picking in two unconfirmed pickings
[stock_transfer_split_multi](stock_transfer_split_multi/) | 8.0.1.0.0 (unported) | In the stock transfer wizard, you can split by multiple units

[//]: # (end addons)
