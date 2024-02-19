
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/stock-logistics-workflow&target_branch=13.0)
[![Pre-commit Status](https://github.com/OCA/stock-logistics-workflow/actions/workflows/pre-commit.yml/badge.svg?branch=13.0)](https://github.com/OCA/stock-logistics-workflow/actions/workflows/pre-commit.yml?query=branch%3A13.0)
[![Build Status](https://github.com/OCA/stock-logistics-workflow/actions/workflows/test.yml/badge.svg?branch=13.0)](https://github.com/OCA/stock-logistics-workflow/actions/workflows/test.yml?query=branch%3A13.0)
[![codecov](https://codecov.io/gh/OCA/stock-logistics-workflow/branch/13.0/graph/badge.svg)](https://codecov.io/gh/OCA/stock-logistics-workflow)
[![Translation Status](https://translation.odoo-community.org/widgets/stock-logistics-workflow-13-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/stock-logistics-workflow-13-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# Odoo Stock Logistic Workflow

This project aims to deal with modules related to manage logistic flows. You'll find modules that:

 - Bring support for picking dispatch
 - Hold picking (adding a step in their workflow)
 - Ease the flow creation for the stock_location official module
 - Add filter to manage packing and deliveries

Please don't hesitate to suggest one of your module to this project. Also, you may want to have a look on those other projects here:

 - https://github.com/OCA/stock-logistics-tracking
 - https://github.com/OCA/stock-logistics-barcode
 - https://github.com/OCA/stock-logistics-warehouse

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[delivery_package_default_shipping_weight](delivery_package_default_shipping_weight/) | 13.0.1.0.1 |  | Set default package shipping weight according to packaging
[delivery_total_weight_from_packaging](delivery_total_weight_from_packaging/) | 13.0.1.1.2 |  | Include packaging weight on move, transfer and package.
[procurement_auto_create_group_carrier](procurement_auto_create_group_carrier/) | 13.0.1.0.0 |  | Procurement Auto Create Group Carrier
[product_cost_price_avco_sync](product_cost_price_avco_sync/) | 13.0.1.1.1 | [![carlosdauden](https://github.com/carlosdauden.png?size=30px)](https://github.com/carlosdauden) [![sergio-teruel](https://github.com/sergio-teruel.png?size=30px)](https://github.com/sergio-teruel) | Set product cost price from updated moves
[product_cost_price_avco_sync_mrp](product_cost_price_avco_sync_mrp/) | 13.0.1.0.1 |  | Set product cost price from updated moves that implies productions
[product_cost_price_avco_sync_mrp_subcontracting](product_cost_price_avco_sync_mrp_subcontracting/) | 13.0.1.0.1 |  | Set product cost price from updated moves that implies productions
[product_supplierinfo_for_customer_picking](product_supplierinfo_for_customer_picking/) | 13.0.1.0.2 |  | This module makes the product customer code visible in the stock moves of a picking.
[purchase_stock_picking_invoice_link](purchase_stock_picking_invoice_link/) | 13.0.2.0.3 |  | Adds link between purchases, pickings and invoices
[sale_line_returned_qty](sale_line_returned_qty/) | 13.0.1.0.0 |  | Track returned quantity of sale order lines.
[sale_line_returned_qty_mrp](sale_line_returned_qty_mrp/) | 13.0.1.0.1 |  | Track returned quantity of sale order lines for BoM products.
[sale_order_deliverable_rate](sale_order_deliverable_rate/) | 13.0.1.0.0 |  | Rate of deliverable product on a sale order
[sale_order_global_stock_route](sale_order_global_stock_route/) | 13.0.1.0.0 |  | Add the possibility to choose one warehouse path for an order
[sale_stock_mto_as_mts_orderpoint](sale_stock_mto_as_mts_orderpoint/) | 13.0.1.2.3 |  | Materialize need from MTO route through orderpoint
[stock_account_product_run_fifo_hook](stock_account_product_run_fifo_hook/) | 13.0.1.1.0 |  | Add more flexibility in the run fifo method.
[stock_auto_move](stock_auto_move/) | 13.0.1.0.0 |  | Automatic Move Processing
[stock_deferred_assign](stock_deferred_assign/) | 13.0.1.0.0 | [![carlosdauden](https://github.com/carlosdauden.png?size=30px)](https://github.com/carlosdauden) | Assign/Reserve stock moves when scheduled date is after today - config days
[stock_landed_costs_currency](stock_landed_costs_currency/) | 13.0.1.0.0 |  | Stock Landed Costs Currency
[stock_landed_costs_delivery](stock_landed_costs_delivery/) | 13.0.1.0.0 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Stock landed costs delivery
[stock_landed_costs_purchase_auto](stock_landed_costs_purchase_auto/) | 13.0.1.0.0 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Stock landed costs purchase auto
[stock_landed_costs_security](stock_landed_costs_security/) | 13.0.1.2.0 | [![cesar-tecnativa](https://github.com/cesar-tecnativa.png?size=30px)](https://github.com/cesar-tecnativa) | Stock landed costs security
[stock_lock_lot](stock_lock_lot/) | 13.0.1.0.0 |  | Stock Lock Lot
[stock_lot_scrap](stock_lot_scrap/) | 13.0.1.0.1 |  | This module adds a button in Production Lot/Serial Number view form to Scrap all products contained.
[stock_move_assign_picking_hook](stock_move_assign_picking_hook/) | 13.0.1.1.0 |  | Stock Move picking assignment hook
[stock_move_change_source_location](stock_move_change_source_location/) | 13.0.1.0.0 |  | This module allows you to change the source location of a stock move from the picking
[stock_move_line_auto_fill](stock_move_line_auto_fill/) | 13.0.1.0.2 |  | Stock Move Line auto fill
[stock_move_line_reference_link](stock_move_line_reference_link/) | 13.0.1.0.0 |  | Add link in stock move line references.
[stock_move_quick_lot](stock_move_quick_lot/) | 13.0.1.0.0 |  | Set lot name and end date directly on picking operations
[stock_no_negative](stock_no_negative/) | 13.0.1.0.1 |  | Disallow negative stock levels by default
[stock_owner_restriction](stock_owner_restriction/) | 13.0.1.0.0 |  | Do not reserve quantity with assigned owner
[stock_partner_delivery_window](stock_partner_delivery_window/) | 13.0.1.3.2 |  | Define preferred delivery time windows for partners
[stock_picking_assign_serial_final](stock_picking_assign_serial_final/) | 13.0.1.1.1 | [![sergio-teruel](https://github.com/sergio-teruel.png?size=30px)](https://github.com/sergio-teruel) | Generate serial numbers until to a final serial number
[stock_picking_auto_create_lot](stock_picking_auto_create_lot/) | 13.0.1.1.0 | [![sergio-teruel](https://github.com/sergio-teruel.png?size=30px)](https://github.com/sergio-teruel) | Auto create lots for incoming pickings
[stock_picking_back2draft](stock_picking_back2draft/) | 13.0.1.0.0 |  | Reopen cancelled pickings
[stock_picking_backorder_strategy](stock_picking_backorder_strategy/) | 13.0.1.0.1 | [![rousseldenis](https://github.com/rousseldenis.png?size=30px)](https://github.com/rousseldenis) [![mgosai](https://github.com/mgosai.png?size=30px)](https://github.com/mgosai) | Picking backordering strategies
[stock_picking_batch_extended](stock_picking_batch_extended/) | 13.0.1.3.0 | [![gurneyalex](https://github.com/gurneyalex.png?size=30px)](https://github.com/gurneyalex) [![carlosdauden](https://github.com/carlosdauden.png?size=30px)](https://github.com/carlosdauden) [![i-vyshnevska](https://github.com/i-vyshnevska.png?size=30px)](https://github.com/i-vyshnevska) | Allows manage a lot of pickings in batch
[stock_picking_batch_extended_account](stock_picking_batch_extended_account/) | 13.0.1.1.1 | [![ernestotejeda](https://github.com/ernestotejeda.png?size=30px)](https://github.com/ernestotejeda) | Generates invoices when batch is set to Done state
[stock_picking_batch_extended_account_sale_type](stock_picking_batch_extended_account_sale_type/) | 13.0.1.0.0 | [![ernestotejeda](https://github.com/ernestotejeda.png?size=30px)](https://github.com/ernestotejeda) | Generates invoices when batch is set to Done state
[stock_picking_customer_ref](stock_picking_customer_ref/) | 13.0.1.0.0 |  | This module displays the sale reference/description in the pickings
[stock_picking_filter_lot](stock_picking_filter_lot/) | 13.0.1.0.1 |  | In picking out lots' selection, filter lots based on their location
[stock_picking_group_by_partner_by_carrier](stock_picking_group_by_partner_by_carrier/) | 13.0.1.10.2 |  | Stock Picking: group by partner and carrier
[stock_picking_group_by_partner_by_carrier_by_date](stock_picking_group_by_partner_by_carrier_by_date/) | 13.0.1.1.1 |  | Stock Picking: group by partner and carrier and scheduled date
[stock_picking_import_serial_number](stock_picking_import_serial_number/) | 13.0.2.0.0 | [![sergio-teruel](https://github.com/sergio-teruel.png?size=30px)](https://github.com/sergio-teruel) | Import S/N from excel file for incoming pickings
[stock_picking_invoice_link](stock_picking_invoice_link/) | 13.0.2.0.4 |  | Adds link between pickings and invoices
[stock_picking_late_activity](stock_picking_late_activity/) | 13.0.1.0.0 | [![ernestotejeda](https://github.com/ernestotejeda.png?size=30px)](https://github.com/ernestotejeda) | Add an scheduled action that creates late picking activities
[stock_picking_line_sequence](stock_picking_line_sequence/) | 13.0.1.0.1 |  | Manages the order of stock moves by displaying its sequence
[stock_picking_mass_action](stock_picking_mass_action/) | 13.0.1.0.0 |  | Stock Picking Mass Action
[stock_picking_operation_quick_change](stock_picking_operation_quick_change/) | 13.0.1.1.0 |  | Change location of all picking operations
[stock_picking_origin_reference](stock_picking_origin_reference/) | 13.0.1.0.0 |  | Add clickable button to the Transfer Source Document.
[stock_picking_origin_reference_purchase](stock_picking_origin_reference_purchase/) | 13.0.1.0.0 |  | Transfer to Purchase Order navigation from the Source Document.
[stock_picking_origin_reference_sale](stock_picking_origin_reference_sale/) | 13.0.1.0.0 |  | Transfer to Sales Order navigation from the Source Document.
[stock_picking_package_preparation](stock_picking_package_preparation/) | 13.0.1.0.0 |  | Stock Picking Package Preparation
[stock_picking_product_assortment](stock_picking_product_assortment/) | 13.0.1.0.0 | [![CarlosRoca13](https://github.com/CarlosRoca13.png?size=30px)](https://github.com/CarlosRoca13) | Stock Picking Product Assortment
[stock_picking_product_assortment_availability_inline](stock_picking_product_assortment_availability_inline/) | 13.0.1.0.0 | [![Sergio-teruel](https://github.com/Sergio-teruel.png?size=30px)](https://github.com/Sergio-teruel) | Glue module to display stock available when an assortment is defined for a partner
[stock_picking_product_availability_inline](stock_picking_product_availability_inline/) | 13.0.1.1.1 |  | Show product availability in product drop-down in stock picking form view.
[stock_picking_purchase_order_link](stock_picking_purchase_order_link/) | 13.0.1.0.0 |  | Link between picking and purchase order
[stock_picking_restrict_cancel_with_orig_move](stock_picking_restrict_cancel_with_orig_move/) | 13.0.1.0.1 |  | Restrict cancellation of dest moves according to origin.
[stock_picking_return_restricted_qty](stock_picking_return_restricted_qty/) | 13.0.1.0.1 |  | Restrict the return to delivered quantity
[stock_picking_sale_order_link](stock_picking_sale_order_link/) | 13.0.1.0.1 |  | Link between picking and sale order
[stock_picking_send_by_mail](stock_picking_send_by_mail/) | 13.0.1.2.0 |  | Send stock picking by email
[stock_picking_show_backorder](stock_picking_show_backorder/) | 13.0.1.0.1 |  | Provides a new field on stock pickings, allowing to display the corresponding backorders.
[stock_picking_show_return](stock_picking_show_return/) | 13.0.1.0.0 |  | Show returns on stock pickings
[stock_picking_warn_message](stock_picking_warn_message/) | 13.0.1.0.2 |  | Add a popup warning on picking to ensure warning is populated
[stock_picking_whole_scrap](stock_picking_whole_scrap/) | 13.0.1.0.0 | [![sergio-teruel](https://github.com/sergio-teruel.png?size=30px)](https://github.com/sergio-teruel) | Create whole scrap from a picking for move lines
[stock_production_lot_active](stock_production_lot_active/) | 13.0.1.0.0 | [![ThomasBinsfeld](https://github.com/ThomasBinsfeld.png?size=30px)](https://github.com/ThomasBinsfeld) | Allow to archive/unarchive a lot.
[stock_push_delay](stock_push_delay/) | 13.0.1.0.1 |  | Manual evaluation of Push rules
[stock_putaway_by_route](stock_putaway_by_route/) | 13.0.1.2.0 |  | Add a match by route on putaway, after product and categories
[stock_putaway_hook](stock_putaway_hook/) | 13.0.1.1.0 |  | Add hooks allowing modules to add more putaway strategies
[stock_quant_package_dimension](stock_quant_package_dimension/) | 13.0.1.1.0 |  | Use dimensions on packages
[stock_quant_package_dimension_total_weight_from_packaging](stock_quant_package_dimension_total_weight_from_packaging/) | 13.0.1.1.0 |  | Estimated weight of a package
[stock_quant_package_product_packaging](stock_quant_package_product_packaging/) | 13.0.1.1.0 |  | Use product packagings on packages
[stock_return_request](stock_return_request/) | 13.0.1.1.1 |  | Stock Return Request
[stock_scrap_cancel](stock_scrap_cancel/) | 13.0.1.0.0 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Stock Scrap Cancel
[stock_split_picking](stock_split_picking/) | 13.0.2.1.1 |  | Split a picking in two not transferred pickings
[stock_valuation_layer_usage](stock_valuation_layer_usage/) | 13.0.1.1.0 |  | Trace where has the stock valuation been used in, including the quantities taken.

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
