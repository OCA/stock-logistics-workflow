[![Build Status](https://travis-ci.org/OCA/stock-logistics-workflow.svg?branch=10.0)](https://travis-ci.org/OCA/stock-logistics-workflow)
[![Coverage Status](https://img.shields.io/coveralls/OCA/stock-logistics-workflow.svg)](https://coveralls.io/r/OCA/stock-logistics-workflow?branch=10.0)

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
[product_expiry_simple](product_expiry_simple/) | 10.0.1.0.0 | Simpler and better alternative to the official product_expiry module
[stock_auto_move](stock_auto_move/) | 10.0.1.0.0 | Automatic Move Processing
[stock_ownership_availability_rules](stock_ownership_availability_rules/) | 10.0.1.0.0 | Enforce ownership on stock availability
[stock_ownership_by_move](stock_ownership_by_move/) | 10.0.0.1.0 | Preserve Ownership of moves (not pickings) on reception.
[stock_picking_package_preparation](stock_picking_package_preparation/) | 10.0.1.0.1 | Stock Picking Package Preparation
[stock_picking_package_preparation_line](stock_picking_package_preparation_line/) | 10.0.1.0.1 | Stock Picking Package Preparation Line
[stock_picking_show_return](stock_picking_show_return/) | 10.0.1.0.0 | Show returns on stock pickings
[stock_split_picking](stock_split_picking/) | 10.0.1.0.0 | Split a picking in two not transferred pickings


Unported addons
---------------
addon | version | summary
--- | --- | ---
[picking_dispatch_wave](picking_dispatch_wave/) | 0.1 (unported) | Picking Dispatch Wave
[product_customer_code_picking](product_customer_code_picking/) | 1.0 (unported) | Product Customer code for stock picking
[product_serial](product_serial/) | 1.0 (unported) | Enhance Serial Number management
[stock_batch_picking](stock_batch_picking/) | 9.0.1.0.0 (unported) | Stock batch picking
[stock_cancel](stock_cancel/) | 1.2 (unported) | Stock Cancel
[stock_dropshipping_dual_invoice](stock_dropshipping_dual_invoice/) | 8.0.0.1.0 (unported) | Create both Supplier and Customer Invoices from a Dropshipping Delivery
[stock_inventory_retry_assign](stock_inventory_retry_assign/) | 1.0 (unported) | Check Availability after Inventories
[stock_location_flow_creator](stock_location_flow_creator/) | 1.0 (unported) | Create configuration of stock location flow
[stock_move_backdating](stock_move_backdating/) | 1.0 (unported) | Allows back-dating of stock moves
[stock_move_description](stock_move_description/) | 8.0.1.0.0 (unported) | Stock move description
[stock_move_on_hold](stock_move_on_hold/) | 1.0 (unported) | Stock On Hold Status
[stock_obsolete](stock_obsolete/) | 1.0 (unported) | Add product depreciation
[stock_picking_backorder_strategy](stock_picking_backorder_strategy/) | 8.0.0.1.0 (unported) | Picking backordering strategies
[stock_picking_compute_delivery_date](stock_picking_compute_delivery_date/) | 8.0.1.1.0 (unported) | Stock Picking Compute Delivery Date
[stock_picking_deliver_uos](stock_picking_deliver_uos/) | 8.0.1.0.0 (unported) | Adds fields uos and uos_quantity to Stock Transfer Details
[stock_picking_invoice_link](stock_picking_invoice_link/) | 8.0.1.0.0 (unported) | Adds link between pickings and generated invoices
[stock_picking_mass_assign](stock_picking_mass_assign/) | 9.0.1.0.0 (unported) | Delivery Orders Mass Assign
[stock_picking_priority](stock_picking_priority/) | 0.2 (unported) | Picking Priority
[stock_picking_reorder_lines](stock_picking_reorder_lines/) | 8.0.0.1.0 (unported) | Provide a new field on stock moves, allowing to manage the orders of moves in a picking.
[stock_sale_filters](stock_sale_filters/) | 1.3 (unported) | SO related filters on stock.picking and sale.order
[stock_transfer_split_multi](stock_transfer_split_multi/) | 8.0.1.0.0 (unported) | In the stock transfer wizard, you can split by multiple units

[//]: # (end addons)
