
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/stock-logistics-workflow&target_branch=15.0)
[![Pre-commit Status](https://github.com/OCA/stock-logistics-workflow/actions/workflows/pre-commit.yml/badge.svg?branch=15.0)](https://github.com/OCA/stock-logistics-workflow/actions/workflows/pre-commit.yml?query=branch%3A15.0)
[![Build Status](https://github.com/OCA/stock-logistics-workflow/actions/workflows/test.yml/badge.svg?branch=15.0)](https://github.com/OCA/stock-logistics-workflow/actions/workflows/test.yml?query=branch%3A15.0)
[![codecov](https://codecov.io/gh/OCA/stock-logistics-workflow/branch/15.0/graph/badge.svg)](https://codecov.io/gh/OCA/stock-logistics-workflow)
[![Translation Status](https://translation.odoo-community.org/widgets/stock-logistics-workflow-15-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/stock-logistics-workflow-15-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# stock-logistics-workflow

TODO: add repo description.

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[delivery_procurement_group_carrier](delivery_procurement_group_carrier/) | 15.0.1.0.0 |  | Delivery Procurement Group Carrier
[product_cost_price_avco_sync](product_cost_price_avco_sync/) | 15.0.1.0.4 | [![carlosdauden](https://github.com/carlosdauden.png?size=30px)](https://github.com/carlosdauden) [![sergio-teruel](https://github.com/sergio-teruel.png?size=30px)](https://github.com/sergio-teruel) | Set product cost price from updated moves
[product_supplierinfo_for_customer_picking](product_supplierinfo_for_customer_picking/) | 15.0.1.0.0 |  | This module makes the product customer code visible in the stock moves of a picking.
[purchase_stock_picking_invoice_link](purchase_stock_picking_invoice_link/) | 15.0.1.0.0 |  | Adds link between purchases, pickings and invoices
[sale_line_returned_qty](sale_line_returned_qty/) | 15.0.1.0.0 |  | Track returned quantity of sale order lines.
[sale_line_returned_qty_mrp](sale_line_returned_qty_mrp/) | 15.0.1.0.1 |  | Track returned quantity of sale order lines for BoM products.
[sale_order_global_stock_route](sale_order_global_stock_route/) | 15.0.1.0.0 |  | Add the possibility to choose one warehouse path for an order
[stock_account_product_run_fifo_hook](stock_account_product_run_fifo_hook/) | 15.0.1.0.3 |  | Add more flexibility in the run fifo method.
[stock_auto_move](stock_auto_move/) | 15.0.1.0.0 |  | Automatic Move Processing
[stock_delivery_note](stock_delivery_note/) | 15.0.1.0.0 |  | This module allows to fill in a delivery note that will be displayed on delivery report
[stock_force_assign_by_type](stock_force_assign_by_type/) | 15.0.1.0.1 |  | Force stock allocation based on the picking operation type in Odoo
[stock_landed_costs_delivery](stock_landed_costs_delivery/) | 15.0.2.0.1 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Stock landed costs delivery
[stock_landed_costs_priority](stock_landed_costs_priority/) | 15.0.1.0.0 |  | Add priority to landed costs
[stock_landed_costs_purchase_auto](stock_landed_costs_purchase_auto/) | 15.0.2.0.0 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Stock landed costs purchase auto
[stock_landed_costs_security](stock_landed_costs_security/) | 15.0.1.0.0 | [![cesar-tecnativa](https://github.com/cesar-tecnativa.png?size=30px)](https://github.com/cesar-tecnativa) | Stock landed costs security
[stock_lot_on_hand_first](stock_lot_on_hand_first/) | 15.0.1.0.0 | [![grindtildeath](https://github.com/grindtildeath.png?size=30px)](https://github.com/grindtildeath) | Allows to display lots on hand first in M2o fields
[stock_lot_product_qty_search](stock_lot_product_qty_search/) | 15.0.1.0.0 | [![grindtildeath](https://github.com/grindtildeath.png?size=30px)](https://github.com/grindtildeath) | Allows to search on Quantity field of Lot/Serial Numbers
[stock_move_change_source_location](stock_move_change_source_location/) | 15.0.1.0.0 |  | This module allows you to change the source location of a stock move from the picking
[stock_move_consu_location_from_putaway](stock_move_consu_location_from_putaway/) | 15.0.1.0.0 | [![grindtildeath](https://github.com/grindtildeath.png?size=30px)](https://github.com/grindtildeath) | Use putaway location as source of move lines for consumables
[stock_move_line_auto_fill](stock_move_line_auto_fill/) | 15.0.1.0.1 |  | Stock Move Line auto fill
[stock_move_name_from_sale_line](stock_move_name_from_sale_line/) | 15.0.1.0.0 |  | Set stock move name from sale line name
[stock_move_original_date](stock_move_original_date/) | 15.0.1.0.0 | [![LoisRForgeFlow](https://github.com/LoisRForgeFlow.png?size=30px)](https://github.com/LoisRForgeFlow) | adds the Original Date Scheduled to stock moves.
[stock_move_propagate_first_move](stock_move_propagate_first_move/) | 15.0.1.0.0 |  | This addon propagate the picking type of the original move to all next moves created from procurement
[stock_move_quick_lot](stock_move_quick_lot/) | 15.0.1.0.0 |  | Set lot name and end date directly on picking operations
[stock_no_negative](stock_no_negative/) | 15.0.1.0.0 |  | Disallow negative stock levels by default
[stock_owner_restriction](stock_owner_restriction/) | 15.0.1.1.4 |  | Do not reserve quantity with assigned owner
[stock_picking_assign_serial_final](stock_picking_assign_serial_final/) | 15.0.1.0.0 | [![sergio-teruel](https://github.com/sergio-teruel.png?size=30px)](https://github.com/sergio-teruel) | Generate serial numbers until to a final serial number
[stock_picking_auto_create_lot](stock_picking_auto_create_lot/) | 15.0.2.0.0 | [![sergio-teruel](https://github.com/sergio-teruel.png?size=30px)](https://github.com/sergio-teruel) | Auto create lots for incoming pickings
[stock_picking_back2draft](stock_picking_back2draft/) | 15.0.1.0.1 |  | Reopen cancelled pickings
[stock_picking_backorder_strategy](stock_picking_backorder_strategy/) | 15.0.1.0.0 | [![rousseldenis](https://github.com/rousseldenis.png?size=30px)](https://github.com/rousseldenis) [![mgosai](https://github.com/mgosai.png?size=30px)](https://github.com/mgosai) | Picking backordering strategies
[stock_picking_batch_extended](stock_picking_batch_extended/) | 15.0.2.5.0 | [![gurneyalex](https://github.com/gurneyalex.png?size=30px)](https://github.com/gurneyalex) [![carlosdauden](https://github.com/carlosdauden.png?size=30px)](https://github.com/carlosdauden) [![i-vyshnevska](https://github.com/i-vyshnevska.png?size=30px)](https://github.com/i-vyshnevska) | Allows manage a lot of pickings in batch
[stock_picking_batch_extended_account](stock_picking_batch_extended_account/) | 15.0.1.0.2 | [![ernestotejeda](https://github.com/ernestotejeda.png?size=30px)](https://github.com/ernestotejeda) | Generates invoices when batch is set to Done state
[stock_picking_batch_extended_account_sale_type](stock_picking_batch_extended_account_sale_type/) | 15.0.1.0.1 | [![ernestotejeda](https://github.com/ernestotejeda.png?size=30px)](https://github.com/ernestotejeda) | Generates invoices when batch is set to Done state
[stock_picking_batch_operation_quick_change](stock_picking_batch_operation_quick_change/) | 15.0.1.0.0 | [![sergio-teruel](https://github.com/sergio-teruel.png?size=30px)](https://github.com/sergio-teruel) | Change location of all picking batch operations
[stock_picking_batch_outgoing](stock_picking_batch_outgoing/) | 15.0.1.2.0 | [![sergio-teruel](https://github.com/sergio-teruel.png?size=30px)](https://github.com/sergio-teruel) | Allows set on pickings the batch picking from last picking (out)
[stock_picking_batch_set_quantity](stock_picking_batch_set_quantity/) | 15.0.1.1.0 |  | Adds buttons to set all reserved quantity in quantity done fields
[stock_picking_customer_ref](stock_picking_customer_ref/) | 15.0.1.0.0 |  | This module displays the sale reference/description in the pickings
[stock_picking_filter_lot](stock_picking_filter_lot/) | 15.0.1.0.1 |  | In picking out lots' selection, filter lots based on their location
[stock_picking_import_serial_number](stock_picking_import_serial_number/) | 15.0.2.0.0 | [![sergio-teruel](https://github.com/sergio-teruel.png?size=30px)](https://github.com/sergio-teruel) | Import S/N from excel file for incoming pickings
[stock_picking_info_lot](stock_picking_info_lot/) | 15.0.1.0.0 |  | Add lot information on Stock Transfer lines
[stock_picking_invoice_link](stock_picking_invoice_link/) | 15.0.1.3.1 |  | Adds link between pickings and invoices
[stock_picking_line_sequence](stock_picking_line_sequence/) | 15.0.1.0.2 |  | Manages the order of stock moves by displaying its sequence
[stock_picking_mass_action](stock_picking_mass_action/) | 15.0.1.0.3 |  | Stock Picking Mass Action
[stock_picking_operation_manual_lot_selection](stock_picking_operation_manual_lot_selection/) | 15.0.1.0.0 |  | Stock Picking Operation Manual Lot Selection
[stock_picking_operation_quick_change](stock_picking_operation_quick_change/) | 15.0.1.1.1 |  | Change location of all picking operations
[stock_picking_origin_reference](stock_picking_origin_reference/) | 15.0.1.0.0 |  | Add clickable button to the Transfer Source Document.
[stock_picking_origin_reference_purchase](stock_picking_origin_reference_purchase/) | 15.0.1.0.0 |  | Transfer to Purchase Order navigation from the Source Document.
[stock_picking_origin_reference_sale](stock_picking_origin_reference_sale/) | 15.0.1.0.0 |  | Transfer to Sales Order navigation from the Source Document.
[stock_picking_product_assortment](stock_picking_product_assortment/) | 15.0.2.0.0 | [![CarlosRoca13](https://github.com/CarlosRoca13.png?size=30px)](https://github.com/CarlosRoca13) | Stock Picking Product Assortment
[stock_picking_product_assortment_availability_inline](stock_picking_product_assortment_availability_inline/) | 15.0.2.0.0 | [![Sergio-teruel](https://github.com/Sergio-teruel.png?size=30px)](https://github.com/Sergio-teruel) | Glue module to display stock available when an assortment is defined for a partner
[stock_picking_product_availability_inline](stock_picking_product_availability_inline/) | 15.0.1.0.1 |  | Show product availability in product drop-down in stock picking form view.
[stock_picking_product_availability_search](stock_picking_product_availability_search/) | 15.0.1.0.1 | [![ivantodorovich](https://github.com/ivantodorovich.png?size=30px)](https://github.com/ivantodorovich) | Filter pickings by their products availability state
[stock_picking_propagate_scheduled_date](stock_picking_propagate_scheduled_date/) | 15.0.1.0.1 |  | Propagate Stock Picking Scheduled Date
[stock_picking_purchase_order_link](stock_picking_purchase_order_link/) | 15.0.1.0.1 |  | Link between picking and purchase order
[stock_picking_return_restricted_qty](stock_picking_return_restricted_qty/) | 15.0.1.0.1 |  | Restrict the return to delivered quantity
[stock_picking_sale_order_link](stock_picking_sale_order_link/) | 15.0.1.0.3 |  | Link between picking and sale order
[stock_picking_send_by_mail](stock_picking_send_by_mail/) | 15.0.1.0.2 |  | Send stock picking by email
[stock_picking_show_backorder](stock_picking_show_backorder/) | 15.0.1.0.1 |  | Provides a new field on stock pickings, allowing to display the corresponding backorders.
[stock_picking_show_lot](stock_picking_show_lot/) | 15.0.1.0.0 |  | Stock Picking Show Lot
[stock_picking_show_return](stock_picking_show_return/) | 15.0.1.0.0 |  | Show returns on stock pickings
[stock_picking_start](stock_picking_start/) | 15.0.1.0.0 |  | Add button to start picking
[stock_picking_warn_message](stock_picking_warn_message/) | 15.0.1.0.1 |  | Add a popup warning on picking to ensure warning is populated
[stock_picking_whole_scrap](stock_picking_whole_scrap/) | 15.0.1.0.2 | [![sergio-teruel](https://github.com/sergio-teruel.png?size=30px)](https://github.com/sergio-teruel) | Create whole scrap from a picking for move lines
[stock_product_set](stock_product_set/) | 15.0.1.0.0 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Add product sets in pickings
[stock_production_lot_active](stock_production_lot_active/) | 15.0.1.0.2 | [![ThomasBinsfeld](https://github.com/ThomasBinsfeld.png?size=30px)](https://github.com/ThomasBinsfeld) | Allow to archive/unarchive a lot.
[stock_production_lot_traceability](stock_production_lot_traceability/) | 15.0.1.0.1 | [![ivantodorovich](https://github.com/ivantodorovich.png?size=30px)](https://github.com/ivantodorovich) | Drill down/up the lots produced or consumed
[stock_push_delay](stock_push_delay/) | 15.0.1.0.0 |  | Manual evaluation of Push rules
[stock_putaway_hook](stock_putaway_hook/) | 15.0.1.0.0 |  | Add hooks allowing modules to add more putaway strategies
[stock_receipt_lot_info](stock_receipt_lot_info/) | 15.0.1.1.0 |  | Be able to introduce more info on lot/serial number while processing a receipt.
[stock_reception_discrepancy_distribution](stock_reception_discrepancy_distribution/) | 15.0.1.0.1 |  | Change demand in stock moves linked to reception one
[stock_remote_measure](stock_remote_measure/) | 15.0.1.0.0 | [![chienandalu](https://github.com/chienandalu.png?size=30px)](https://github.com/chienandalu) | Allows to connect to remote devices to record measures in stock fields
[stock_restrict_lot](stock_restrict_lot/) | 15.0.0.1.0 | [![florian-dacosta](https://github.com/florian-dacosta.png?size=30px)](https://github.com/florian-dacosta) | Base module that add back the concept of restrict lot on stock move
[stock_return_request](stock_return_request/) | 15.0.1.0.2 |  | Stock Return Request
[stock_scrap_tier_validation](stock_scrap_tier_validation/) | 15.0.1.0.0 |  | Stock Scrap Tier Validation
[stock_split_picking](stock_split_picking/) | 15.0.1.1.2 |  | Split a picking in two not transferred pickings
[stock_valuation_fifo_lot](stock_valuation_fifo_lot/) | 15.0.1.0.0 | [![newtratip](https://github.com/newtratip.png?size=30px)](https://github.com/newtratip) | Stock Valuation Fifo Lot
[stock_valuation_layer_usage](stock_valuation_layer_usage/) | 15.0.1.1.0 |  | Trace where has the stock valuation been used in, including the quantities taken.
[stock_warn_option](stock_warn_option/) | 15.0.1.0.0 | [![Shide](https://github.com/Shide.png?size=30px)](https://github.com/Shide) [![rafaelbn](https://github.com/rafaelbn.png?size=30px)](https://github.com/rafaelbn) | Add Options to Stock Warn Messages

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
