
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/stock-logistics-workflow&target_branch=18.0)
[![Pre-commit Status](https://github.com/OCA/stock-logistics-workflow/actions/workflows/pre-commit.yml/badge.svg?branch=18.0)](https://github.com/OCA/stock-logistics-workflow/actions/workflows/pre-commit.yml?query=branch%3A18.0)
[![Build Status](https://github.com/OCA/stock-logistics-workflow/actions/workflows/test.yml/badge.svg?branch=18.0)](https://github.com/OCA/stock-logistics-workflow/actions/workflows/test.yml?query=branch%3A18.0)
[![codecov](https://codecov.io/gh/OCA/stock-logistics-workflow/branch/18.0/graph/badge.svg)](https://codecov.io/gh/OCA/stock-logistics-workflow)
[![Translation Status](https://translation.odoo-community.org/widgets/stock-logistics-workflow-18-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/stock-logistics-workflow-18-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# Stock Workflow

Enhance the way flows and processes are working. Find here modules that do not have their place in the other more specialized repositories.

Are you looking for modules related to logistics? Or would like to contribute
to? There are many repositories with specific purposes. Have a look at this
[README](https://github.com/OCA/wms/blob/18.0/README.md).

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[delivery_procurement_group_carrier](delivery_procurement_group_carrier/) | 18.0.1.0.2 |  | Delivery Procurement Group Carrier
[delivery_total_weight_from_packaging](delivery_total_weight_from_packaging/) | 18.0.1.1.0 |  | Include packaging weight on move, transfer and package.
[procurement_auto_create_group_carrier](procurement_auto_create_group_carrier/) | 18.0.1.0.0 |  | Procurement Auto Create Group Carrier
[product_cost_price_avco_sync](product_cost_price_avco_sync/) | 18.0.1.0.0 | <a href='https://github.com/carlosdauden'><img src='https://github.com/carlosdauden.png' width='32' height='32' style='border-radius:50%;' alt='carlosdauden'/></a> <a href='https://github.com/sergio-teruel'><img src='https://github.com/sergio-teruel.png' width='32' height='32' style='border-radius:50%;' alt='sergio-teruel'/></a> | Set product cost price from updated moves
[product_customerinfo_picking](product_customerinfo_picking/) | 18.0.1.0.0 |  | This module makes the product customer code visible in the stock moves of a picking.
[purchase_stock_picking_invoice_link](purchase_stock_picking_invoice_link/) | 18.0.2.0.0 |  | Adds link between purchases, pickings and invoices
[sale_line_returned_qty](sale_line_returned_qty/) | 18.0.1.0.0 |  | Track returned quantity of sale order lines.
[sale_line_returned_qty_mrp](sale_line_returned_qty_mrp/) | 18.0.1.0.0 |  | Track returned quantity of sale order lines for BoM products.
[sale_order_global_stock_route](sale_order_global_stock_route/) | 18.0.1.0.0 |  | Add the possibility to choose one warehouse path for an order
[sale_stock_picking_invoice_link](sale_stock_picking_invoice_link/) | 18.0.1.0.0 |  | Adds link between pickings and invoices
[scrap_reason_code](scrap_reason_code/) | 18.0.1.0.0 | <a href='https://github.com/bodedra'><img src='https://github.com/bodedra.png' width='32' height='32' style='border-radius:50%;' alt='bodedra'/></a> | Reason code for scrapping
[stock_account_product_run_fifo_hook](stock_account_product_run_fifo_hook/) | 18.0.1.0.1 |  | Add more flexibility in the run fifo method.
[stock_checkout_sync](stock_checkout_sync/) | 18.0.1.0.1 |  | Sync location for Checkout operations
[stock_dangerous_goods](stock_dangerous_goods/) | 18.0.1.0.0 | <a href='https://github.com/mmequignon'><img src='https://github.com/mmequignon.png' width='32' height='32' style='border-radius:50%;' alt='mmequignon'/></a> | Adds utility fields to manage dangerous goods
[stock_dynamic_routing](stock_dynamic_routing/) | 18.0.1.1.0 | <a href='https://github.com/jbaudoux'><img src='https://github.com/jbaudoux.png' width='32' height='32' style='border-radius:50%;' alt='jbaudoux'/></a> | Dynamic routing of stock moves
[stock_dynamic_routing_delivery](stock_dynamic_routing_delivery/) | 18.0.1.1.0 | <a href='https://github.com/ivantodorovich'><img src='https://github.com/ivantodorovich.png' width='32' height='32' style='border-radius:50%;' alt='ivantodorovich'/></a> <a href='https://github.com/jbaudoux'><img src='https://github.com/jbaudoux.png' width='32' height='32' style='border-radius:50%;' alt='jbaudoux'/></a> | Glue module between stock dynamic routing and delivery
[stock_dynamic_routing_delivery_procurement_group_carrier](stock_dynamic_routing_delivery_procurement_group_carrier/) | 18.0.1.1.0 | <a href='https://github.com/ivantodorovich'><img src='https://github.com/ivantodorovich.png' width='32' height='32' style='border-radius:50%;' alt='ivantodorovich'/></a> <a href='https://github.com/jbaudoux'><img src='https://github.com/jbaudoux.png' width='32' height='32' style='border-radius:50%;' alt='jbaudoux'/></a> | Use the carrier set on the procurement group for propagation
[stock_dynamic_routing_reserve_rule](stock_dynamic_routing_reserve_rule/) | 18.0.1.0.0 |  | Glue module between dynamic routing and reservation rules
[stock_landed_costs_priority](stock_landed_costs_priority/) | 18.0.1.0.0 |  | Add priority to landed costs
[stock_landed_costs_purchase_auto](stock_landed_costs_purchase_auto/) | 18.0.1.0.0 | <a href='https://github.com/victoralmau'><img src='https://github.com/victoralmau.png' width='32' height='32' style='border-radius:50%;' alt='victoralmau'/></a> | Stock landed costs purchase auto
[stock_lock_lot](stock_lock_lot/) | 18.0.1.0.0 |  | Stock Lock Lot
[stock_move_actual_date](stock_move_actual_date/) | 18.0.1.0.0 | <a href='https://github.com/yostashiro'><img src='https://github.com/yostashiro.png' width='32' height='32' style='border-radius:50%;' alt='yostashiro'/></a> <a href='https://github.com/aungkokolin1997'><img src='https://github.com/aungkokolin1997.png' width='32' height='32' style='border-radius:50%;' alt='aungkokolin1997'/></a> | Stock Move Actual Date
[stock_move_auto_assign_auto_release](stock_move_auto_assign_auto_release/) | 18.0.1.0.1 |  | Auto release moves after auto assign
[stock_move_line_change_lot](stock_move_line_change_lot/) | 18.0.1.0.0 |  | Stock Move Line Change Lot
[stock_move_line_qty_picked](stock_move_line_qty_picked/) | 18.0.1.2.1 | <a href='https://github.com/grindtildeath'><img src='https://github.com/grindtildeath.png' width='32' height='32' style='border-radius:50%;' alt='grindtildeath'/></a> <a href='https://github.com/jbaudoux'><img src='https://github.com/jbaudoux.png' width='32' height='32' style='border-radius:50%;' alt='jbaudoux'/></a> | Separate quantity picked from the reserved quantity
[stock_move_original_date](stock_move_original_date/) | 18.0.1.0.0 | <a href='https://github.com/LoisRForgeFlow'><img src='https://github.com/LoisRForgeFlow.png' width='32' height='32' style='border-radius:50%;' alt='LoisRForgeFlow'/></a> | adds the Original Date Scheduled to stock moves.
[stock_move_quantity_product_uom](stock_move_quantity_product_uom/) | 18.0.1.0.2 |  | computes stock.move's quantity in the uom of the product.
[stock_move_source_relocate](stock_move_source_relocate/) | 18.0.1.0.0 | <a href='https://github.com/jbaudoux'><img src='https://github.com/jbaudoux.png' width='32' height='32' style='border-radius:50%;' alt='jbaudoux'/></a> | Change source location of unavailable moves
[stock_move_source_relocate_dynamic_routing](stock_move_source_relocate_dynamic_routing/) | 18.0.1.0.1 | <a href='https://github.com/jbaudoux'><img src='https://github.com/jbaudoux.png' width='32' height='32' style='border-radius:50%;' alt='jbaudoux'/></a> | Glue module
[stock_no_negative](stock_no_negative/) | 18.0.1.0.2 |  | Disallow negative stock levels by default
[stock_owner_restriction](stock_owner_restriction/) | 18.0.1.0.0 |  | Do not reserve quantity with assigned owner
[stock_partner_delivery_window](stock_partner_delivery_window/) | 18.0.1.2.1 | <a href='https://github.com/jbaudoux'><img src='https://github.com/jbaudoux.png' width='32' height='32' style='border-radius:50%;' alt='jbaudoux'/></a> | Define preferred delivery time windows for partners
[stock_picking_auto_create_lot](stock_picking_auto_create_lot/) | 18.0.1.0.0 | <a href='https://github.com/sergio-teruel'><img src='https://github.com/sergio-teruel.png' width='32' height='32' style='border-radius:50%;' alt='sergio-teruel'/></a> | Auto create lots for incoming pickings
[stock_picking_back2draft](stock_picking_back2draft/) | 18.0.1.0.0 |  | Reopen canceled transfers
[stock_picking_backorder_strategy_cancel](stock_picking_backorder_strategy_cancel/) | 18.0.1.0.0 | <a href='https://github.com/rousseldenis'><img src='https://github.com/rousseldenis.png' width='32' height='32' style='border-radius:50%;' alt='rousseldenis'/></a> <a href='https://github.com/mgosai'><img src='https://github.com/mgosai.png' width='32' height='32' style='border-radius:50%;' alt='mgosai'/></a> | Picking backordering strategies
[stock_picking_batch_creation](stock_picking_batch_creation/) | 18.0.1.2.0 | <a href='https://github.com/lmignon'><img src='https://github.com/lmignon.png' width='32' height='32' style='border-radius:50%;' alt='lmignon'/></a> | Create a batch of pickings to be processed all together
[stock_picking_batch_creation_split_kit](stock_picking_batch_creation_split_kit/) | 18.0.1.0.0 | <a href='https://github.com/ivantodorovich'><img src='https://github.com/ivantodorovich.png' width='32' height='32' style='border-radius:50%;' alt='ivantodorovich'/></a> <a href='https://github.com/TDu'><img src='https://github.com/TDu.png' width='32' height='32' style='border-radius:50%;' alt='TDu'/></a> <a href='https://github.com/jbaudoux'><img src='https://github.com/jbaudoux.png' width='32' height='32' style='border-radius:50%;' alt='jbaudoux'/></a> | Split picking by kit quantity when exceeding limits
[stock_picking_batch_invoice_frequency](stock_picking_batch_invoice_frequency/) | 18.0.1.0.1 | <a href='https://github.com/EmilioPascual'><img src='https://github.com/EmilioPascual.png' width='32' height='32' style='border-radius:50%;' alt='EmilioPascual'/></a> <a href='https://github.com/rafaelbn'><img src='https://github.com/rafaelbn.png' width='32' height='32' style='border-radius:50%;' alt='rafaelbn'/></a> | Invoice Sale Orders from Stock Pickin Batch
[stock_picking_batch_operation_quick_change](stock_picking_batch_operation_quick_change/) | 18.0.1.0.0 | <a href='https://github.com/sergio-teruel'><img src='https://github.com/sergio-teruel.png' width='32' height='32' style='border-radius:50%;' alt='sergio-teruel'/></a> | Change location of all picking batch operations
[stock_picking_batch_planner](stock_picking_batch_planner/) | 18.0.1.0.1 | <a href='https://github.com/EmilioPascual'><img src='https://github.com/EmilioPascual.png' width='32' height='32' style='border-radius:50%;' alt='EmilioPascual'/></a> <a href='https://github.com/Shide'><img src='https://github.com/Shide.png' width='32' height='32' style='border-radius:50%;' alt='Shide'/></a> <a href='https://github.com/rafaelbn'><img src='https://github.com/rafaelbn.png' width='32' height='32' style='border-radius:50%;' alt='rafaelbn'/></a> | Allow planning origin batches/waves from destination batch/wave
[stock_picking_batch_print_invoices](stock_picking_batch_print_invoices/) | 18.0.1.0.1 | <a href='https://github.com/EmilioPascual'><img src='https://github.com/EmilioPascual.png' width='32' height='32' style='border-radius:50%;' alt='EmilioPascual'/></a> | Print invoices from stock picking batchs
[stock_picking_batch_print_pickings](stock_picking_batch_print_pickings/) | 18.0.1.0.1 | <a href='https://github.com/EmilioPascual'><img src='https://github.com/EmilioPascual.png' width='32' height='32' style='border-radius:50%;' alt='EmilioPascual'/></a> | Print Picking from Stock Picking Batch
[stock_picking_batch_validate_confirm](stock_picking_batch_validate_confirm/) | 18.0.1.0.1 | <a href='https://github.com/EmilioPascual'><img src='https://github.com/EmilioPascual.png' width='32' height='32' style='border-radius:50%;' alt='EmilioPascual'/></a> <a href='https://github.com/rafaelbn'><img src='https://github.com/rafaelbn.png' width='32' height='32' style='border-radius:50%;' alt='rafaelbn'/></a> | Request confirmation when validating batch if any pending origin moves
[stock_picking_consolidation_priority](stock_picking_consolidation_priority/) | 18.0.1.0.0 |  | Raise priority of all transfers for a chain when started
[stock_picking_filter_lot](stock_picking_filter_lot/) | 18.0.1.0.0 |  | In picking out lots' selection, filter lots based on their location
[stock_picking_group_by_base](stock_picking_group_by_base/) | 18.0.1.0.0 |  | Allows to define a way to create index on extensible domain
[stock_picking_group_by_partner_by_carrier](stock_picking_group_by_partner_by_carrier/) | 18.0.1.2.5 |  | Stock Picking: group by partner and carrier
[stock_picking_group_by_partner_by_carrier_by_date](stock_picking_group_by_partner_by_carrier_by_date/) | 18.0.1.1.0 |  | Stock Picking: group by partner and carrier and scheduled date
[stock_picking_group_by_partner_by_carrier_force_move_type](stock_picking_group_by_partner_by_carrier_force_move_type/) | 18.0.1.0.0 |  | Glue module for Picking Type Force Shipping Policy and Group Transfers by Partner and Carrier
[stock_picking_invoice_link](stock_picking_invoice_link/) | 18.0.2.0.1 |  | Adds link between pickings and invoices
[stock_picking_kind](stock_picking_kind/) | 18.0.1.0.0 |  | Computes the kind of picking based on locations
[stock_picking_line_sequence](stock_picking_line_sequence/) | 18.0.1.0.1 |  | Manages the order of stock moves by displaying its sequence
[stock_picking_mass_action](stock_picking_mass_action/) | 18.0.1.0.0 |  | Stock Picking Mass Action
[stock_picking_operation_quick_change](stock_picking_operation_quick_change/) | 18.0.1.0.0 |  | Change location of all picking operations
[stock_picking_origin_reference](stock_picking_origin_reference/) | 18.0.1.0.0 |  | Add clickable button to the Transfer Source Document.
[stock_picking_origin_reference_purchase](stock_picking_origin_reference_purchase/) | 18.0.1.0.0 |  | Transfer to Purchase Order navigation from the Source Document.
[stock_picking_origin_reference_sale](stock_picking_origin_reference_sale/) | 18.0.1.0.0 |  | Transfer to Sales Order navigation from the Source Document.
[stock_picking_partner_note](stock_picking_partner_note/) | 18.0.1.0.0 |  | Add partner notes on picking
[stock_picking_progress](stock_picking_progress/) | 18.0.1.0.1 | <a href='https://github.com/mmequignon'><img src='https://github.com/mmequignon.png' width='32' height='32' style='border-radius:50%;' alt='mmequignon'/></a> <a href='https://github.com/JuMiSanAr'><img src='https://github.com/JuMiSanAr.png' width='32' height='32' style='border-radius:50%;' alt='JuMiSanAr'/></a> | Compute the stock.picking progression
[stock_picking_propagate_scheduled_date](stock_picking_propagate_scheduled_date/) | 18.0.1.0.0 |  | Propagate Stock Picking Scheduled Date
[stock_picking_purchase_order_link](stock_picking_purchase_order_link/) | 18.0.1.0.0 |  | Link between picking and purchase order
[stock_picking_restrict_cancel_printed](stock_picking_restrict_cancel_printed/) | 18.0.1.0.0 | <a href='https://github.com/jbaudoux'><img src='https://github.com/jbaudoux.png' width='32' height='32' style='border-radius:50%;' alt='jbaudoux'/></a> | Prevent canceling a stock transfer if printed.
[stock_picking_return_restricted_qty](stock_picking_return_restricted_qty/) | 18.0.1.0.0 |  | Restrict the return to delivered quantity
[stock_picking_sale_order_link](stock_picking_sale_order_link/) | 18.0.1.0.0 |  | Link between picking and sale order
[stock_picking_send_by_mail](stock_picking_send_by_mail/) | 18.0.1.0.0 |  | Send stock picking by email
[stock_picking_show_backorder](stock_picking_show_backorder/) | 18.0.1.0.0 |  | Provides a new field on stock pickings, allowing to display the corresponding backorders.
[stock_picking_show_return](stock_picking_show_return/) | 18.0.1.0.0 |  | Show returns on stock pickings
[stock_picking_tier_validation](stock_picking_tier_validation/) | 18.0.1.0.1 |  | Extends the functionality of Transfers to support a tier validation process.
[stock_picking_type_force_move_type](stock_picking_type_force_move_type/) | 18.0.1.0.1 |  | Force shipping policies on operation types
[stock_picking_warn_message](stock_picking_warn_message/) | 18.0.1.0.0 |  | Add a popup warning on picking to ensure warning is populated
[stock_picking_whole_scrap](stock_picking_whole_scrap/) | 18.0.1.0.0 | <a href='https://github.com/sergio-teruel'><img src='https://github.com/sergio-teruel.png' width='32' height='32' style='border-radius:50%;' alt='sergio-teruel'/></a> | Create whole scrap from a picking for move lines
[stock_product_set](stock_product_set/) | 18.0.1.0.0 | <a href='https://github.com/victoralmau'><img src='https://github.com/victoralmau.png' width='32' height='32' style='border-radius:50%;' alt='victoralmau'/></a> | Add product sets in pickings
[stock_production_lot_active](stock_production_lot_active/) | 18.0.1.0.0 | <a href='https://github.com/ThomasBinsfeld'><img src='https://github.com/ThomasBinsfeld.png' width='32' height='32' style='border-radius:50%;' alt='ThomasBinsfeld'/></a> | Allow to archive/unarchive lots/serial numbers
[stock_receipt_lot_info](stock_receipt_lot_info/) | 18.0.1.0.0 |  | Be able to introduce more info on lot/serial number while processing a receipt.
[stock_restrict_lot](stock_restrict_lot/) | 18.0.1.0.0 | <a href='https://github.com/florian-dacosta'><img src='https://github.com/florian-dacosta.png' width='32' height='32' style='border-radius:50%;' alt='florian-dacosta'/></a> | Base module that add back the concept of restrict lot on stock move
[stock_split_picking](stock_split_picking/) | 18.0.2.1.0 |  | Split a picking in two not transferred pickings
[stock_split_picking_dimension](stock_split_picking_dimension/) | 18.0.1.0.0 |  | Split a picking in two not transferred pickings to ensure that the first one doesn't exceed given dimensions (nbr lines, volume, weight)
[stock_split_picking_kit](stock_split_picking_kit/) | 18.0.1.0.0 |  | Split a picking by a number of kits.
[stock_valuation_layer_usage](stock_valuation_layer_usage/) | 18.0.1.0.0 |  | Trace where has the stock valuation been used in, including the quantities taken.

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to Odoo Community Association (OCA)
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----
OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
