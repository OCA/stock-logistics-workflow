
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/stock-logistics-workflow&target_branch=14.0)
[![Pre-commit Status](https://github.com/OCA/stock-logistics-workflow/actions/workflows/pre-commit.yml/badge.svg?branch=14.0)](https://github.com/OCA/stock-logistics-workflow/actions/workflows/pre-commit.yml?query=branch%3A14.0)
[![Build Status](https://github.com/OCA/stock-logistics-workflow/actions/workflows/test.yml/badge.svg?branch=14.0)](https://github.com/OCA/stock-logistics-workflow/actions/workflows/test.yml?query=branch%3A14.0)
[![codecov](https://codecov.io/gh/OCA/stock-logistics-workflow/branch/14.0/graph/badge.svg)](https://codecov.io/gh/OCA/stock-logistics-workflow)
[![Translation Status](https://translation.odoo-community.org/widgets/stock-logistics-workflow-14-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/stock-logistics-workflow-14-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# stock-logistics-workflow

Odoo Stock, Workflow and Organization

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[delivery_package_default_shipping_weight](delivery_package_default_shipping_weight/) | 14.0.1.0.1 |  | Set default package shipping weight according to packaging
[delivery_procurement_group_carrier](delivery_procurement_group_carrier/) | 14.0.1.1.2 |  | Delivery Procurement Group Carrier
[delivery_total_weight_from_packaging](delivery_total_weight_from_packaging/) | 14.0.1.0.1 |  | Include packaging weight on move, transfer and package.
[procurement_auto_create_group_carrier](procurement_auto_create_group_carrier/) | 14.0.1.1.1 |  | Procurement Auto Create Group Carrier
[product_cost_price_avco_sync](product_cost_price_avco_sync/) | 14.0.1.0.1 | [![carlosdauden](https://github.com/carlosdauden.png?size=30px)](https://github.com/carlosdauden) [![sergio-teruel](https://github.com/sergio-teruel.png?size=30px)](https://github.com/sergio-teruel) | Set product cost price from updated moves
[product_expiry_simple](product_expiry_simple/) | 14.0.1.0.0 | [![alexis-via](https://github.com/alexis-via.png?size=30px)](https://github.com/alexis-via) | Simpler and better alternative to the official product_expiry module
[product_supplierinfo_for_customer_picking](product_supplierinfo_for_customer_picking/) | 14.0.1.4.0 | [![aleuffre](https://github.com/aleuffre.png?size=30px)](https://github.com/aleuffre) [![renda-dev](https://github.com/renda-dev.png?size=30px)](https://github.com/renda-dev) [![PicchiSeba](https://github.com/PicchiSeba.png?size=30px)](https://github.com/PicchiSeba) | This module makes the product customer code visible in the stock moves of a picking.
[product_supplierinfo_picking](product_supplierinfo_picking/) | 14.0.1.0.0 |  | This module makes the product supplier code visible in the stock moves of a picking.
[purchase_stock_picking_invoice_link](purchase_stock_picking_invoice_link/) | 14.0.1.1.0 |  | Adds link between purchases, pickings and invoices
[sale_line_returned_qty](sale_line_returned_qty/) | 14.0.1.0.0 |  | Track returned quantity of sale order lines.
[sale_line_returned_qty_mrp](sale_line_returned_qty_mrp/) | 14.0.1.0.1 |  | Track returned quantity of sale order lines for BoM products.
[sale_order_global_stock_route](sale_order_global_stock_route/) | 14.0.1.0.1 |  | Add the possibility to choose one warehouse path for an order
[sale_purchase_stock_line_note](sale_purchase_stock_line_note/) | 14.0.1.1.0 | [![grindtildeath](https://github.com/grindtildeath.png?size=30px)](https://github.com/grindtildeath) | Propagate sale line note to stock move and purchase
[sale_stock_mto_as_mts_orderpoint](sale_stock_mto_as_mts_orderpoint/) | 14.0.1.0.2 |  | Materialize need from MTO route through orderpoint
[stock_account_product_run_fifo_hook](stock_account_product_run_fifo_hook/) | 14.0.1.0.1 |  | Add more flexibility in the run fifo method.
[stock_auto_move](stock_auto_move/) | 14.0.1.0.0 |  | Automatic Move Processing
[stock_dangerous_goods](stock_dangerous_goods/) | 14.0.1.0.0 | [![mmequignon](https://github.com/mmequignon.png?size=30px)](https://github.com/mmequignon) | Adds utility fields to manage dangerous goods
[stock_delivery_note](stock_delivery_note/) | 14.0.1.0.1 |  | This module allows to fill in a delivery note that will be displayed on delivery report
[stock_landed_costs_delivery](stock_landed_costs_delivery/) | 14.0.1.0.1 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Stock landed costs delivery
[stock_landed_costs_mrp_subcontracting](stock_landed_costs_mrp_subcontracting/) | 14.0.1.1.0 |  | When using Subcontracting, use the incoming shipment in landed costs
[stock_landed_costs_purchase_auto](stock_landed_costs_purchase_auto/) | 14.0.1.0.0 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Stock landed costs purchase auto
[stock_landed_costs_security](stock_landed_costs_security/) | 14.0.1.0.0 | [![cesar-tecnativa](https://github.com/cesar-tecnativa.png?size=30px)](https://github.com/cesar-tecnativa) | Stock landed costs security
[stock_lock_lot](stock_lock_lot/) | 14.0.1.0.0 |  | Stock Lock Lot
[stock_lot_on_hand_first](stock_lot_on_hand_first/) | 14.0.1.0.0 | [![grindtildeath](https://github.com/grindtildeath.png?size=30px)](https://github.com/grindtildeath) | Allows to display lots on hand first in M2o fields
[stock_lot_product_qty_search](stock_lot_product_qty_search/) | 14.0.1.0.0 | [![grindtildeath](https://github.com/grindtildeath.png?size=30px)](https://github.com/grindtildeath) | Allows to search on Quantity field of Lot/Serial Numbers
[stock_lot_production_date](stock_lot_production_date/) | 14.0.1.0.0 |  | Stock Lot Production Date
[stock_lot_scrap](stock_lot_scrap/) | 14.0.1.0.2 |  | This module adds a button in Production Lot/Serial Number view form to Scrap all products contained.
[stock_mass_scrap](stock_mass_scrap/) | 14.0.1.0.1 |  | Add wizard to mass scrap expired products
[stock_move_assign_picking_hook](stock_move_assign_picking_hook/) | 14.0.1.1.2 |  | Stock Move picking assignment hook
[stock_move_backdating](stock_move_backdating/) | 14.0.1.0.1 |  | Stock Move Backdating
[stock_move_change_source_location](stock_move_change_source_location/) | 14.0.1.0.1 |  | This module allows you to change the source location of a stock move from the picking
[stock_move_forced_lot](stock_move_forced_lot/) | 14.0.1.0.0 |  | This module allows you to set a lot_id in a procurement to force the stock move generated to only reserve the selected lot.
[stock_move_free_reservation_reassign](stock_move_free_reservation_reassign/) | 14.0.1.0.0 |  | Try to reassign a move when its reservation is removed due to the related quant becoming unavailable
[stock_move_line_auto_fill](stock_move_line_auto_fill/) | 14.0.1.0.0 |  | Stock Move Line auto fill
[stock_move_quick_lot](stock_move_quick_lot/) | 14.0.1.0.0 |  | Set lot name and end date directly on picking operations
[stock_no_negative](stock_no_negative/) | 14.0.1.0.1 |  | Disallow negative stock levels by default
[stock_owner_restriction](stock_owner_restriction/) | 14.0.1.0.2 |  | Do not reserve quantity with assigned owner
[stock_partner_delivery_window](stock_partner_delivery_window/) | 14.0.1.2.2 |  | Define preferred delivery time windows for partners
[stock_picking_auto_create_lot](stock_picking_auto_create_lot/) | 14.0.1.0.1 | [![sergio-teruel](https://github.com/sergio-teruel.png?size=30px)](https://github.com/sergio-teruel) | Auto create lots for incoming pickings
[stock_picking_auto_create_lot_qty](stock_picking_auto_create_lot_qty/) | 14.0.1.0.0 |  | Auto batch generation by quantity
[stock_picking_auto_create_package](stock_picking_auto_create_package/) | 14.0.1.0.0 |  | Put all move lines in packs on validation.
[stock_picking_back2draft](stock_picking_back2draft/) | 14.0.1.0.0 |  | Reopen cancelled pickings
[stock_picking_backorder_strategy](stock_picking_backorder_strategy/) | 14.0.1.0.0 | [![rousseldenis](https://github.com/rousseldenis.png?size=30px)](https://github.com/rousseldenis) [![mgosai](https://github.com/mgosai.png?size=30px)](https://github.com/mgosai) | Picking backordering strategies
[stock_picking_batch_extended](stock_picking_batch_extended/) | 14.0.1.0.2 | [![gurneyalex](https://github.com/gurneyalex.png?size=30px)](https://github.com/gurneyalex) [![carlosdauden](https://github.com/carlosdauden.png?size=30px)](https://github.com/carlosdauden) [![i-vyshnevska](https://github.com/i-vyshnevska.png?size=30px)](https://github.com/i-vyshnevska) | Allows manage a lot of pickings in batch
[stock_picking_cancel_reason](stock_picking_cancel_reason/) | 14.0.1.0.1 |  | Stock Picking Cancel Reason
[stock_picking_default_planned_transfer](stock_picking_default_planned_transfer/) | 14.0.1.0.1 | [![Kev-Roche](https://github.com/Kev-Roche.png?size=30px)](https://github.com/Kev-Roche) | Set Planned Transfer as Default from Inventory Views
[stock_picking_filter_lot](stock_picking_filter_lot/) | 14.0.2.0.2 |  | In picking out lots' selection, filter lots based on their location
[stock_picking_group_by_partner_by_carrier](stock_picking_group_by_partner_by_carrier/) | 14.0.1.4.4 |  | Stock Picking: group by partner and carrier
[stock_picking_group_by_partner_by_carrier_by_date](stock_picking_group_by_partner_by_carrier_by_date/) | 14.0.1.0.1 |  | Stock Picking: group by partner and carrier and scheduled date
[stock_picking_import_serial_number](stock_picking_import_serial_number/) | 14.0.1.0.1 | [![sergio-teruel](https://github.com/sergio-teruel.png?size=30px)](https://github.com/sergio-teruel) | Import S/N from excel file for incoming pickings
[stock_picking_inter_warehouse](stock_picking_inter_warehouse/) | 14.0.1.2.2 | [![aleuffre](https://github.com/aleuffre.png?size=30px)](https://github.com/aleuffre) [![renda-dev](https://github.com/renda-dev.png?size=30px)](https://github.com/renda-dev) | Stock Picking Inter Warehouse
[stock_picking_invoice_link](stock_picking_invoice_link/) | 14.0.1.2.2 |  | Adds link between pickings and invoices
[stock_picking_line_sequence](stock_picking_line_sequence/) | 14.0.1.0.0 |  | Manages the order of stock moves by displaying its sequence
[stock_picking_mass_action](stock_picking_mass_action/) | 14.0.1.0.2 |  | Stock Picking Mass Action
[stock_picking_partner_note](stock_picking_partner_note/) | 14.0.1.0.1 |  | Add partner notes on picking
[stock_picking_product_link](stock_picking_product_link/) | 14.0.1.0.0 | [![robinkeunen](https://github.com/robinkeunen.png?size=30px)](https://github.com/robinkeunen) | Adds a "Product" smart button on stock pickings.
[stock_picking_progress](stock_picking_progress/) | 14.0.1.2.1 | [![mmequignon](https://github.com/mmequignon.png?size=30px)](https://github.com/mmequignon) [![JuMiSanAr](https://github.com/JuMiSanAr.png?size=30px)](https://github.com/JuMiSanAr) | Compute the stock.picking progression
[stock_picking_purchase_order_link](stock_picking_purchase_order_link/) | 14.0.1.0.1 |  | Link between picking and purchase order
[stock_picking_putinpack_restriction](stock_picking_putinpack_restriction/) | 14.0.1.0.1 |  | Adds a restriction on transfer type to force or disallow the use of destination package.
[stock_picking_quick](stock_picking_quick/) | 14.0.1.0.5 | [![PierrickBrun](https://github.com/PierrickBrun.png?size=30px)](https://github.com/PierrickBrun) [![bealdav](https://github.com/bealdav.png?size=30px)](https://github.com/bealdav) | Quick Stock Picking
[stock_picking_reallocation](stock_picking_reallocation/) | 14.0.1.0.0 |  | Allow to reallocate moves from a picking to several pickings.
[stock_picking_restrict_cancel_printed](stock_picking_restrict_cancel_printed/) | 14.0.1.0.1 |  | Prevent canceling a stock transfer if printed.
[stock_picking_restrict_cancel_with_orig_move](stock_picking_restrict_cancel_with_orig_move/) | 14.0.1.0.1 |  | Restrict cancellation of dest moves according to origin.
[stock_picking_return_lot](stock_picking_return_lot/) | 14.0.1.0.1 |  | Propagate SN/lots from origin picking to return picking.
[stock_picking_return_show_lot](stock_picking_return_show_lot/) | 14.0.1.0.1 |  | This module allows to show lots in the picking return wizard before " "return picking creation.
[stock_picking_sale_order_link](stock_picking_sale_order_link/) | 14.0.1.0.1 |  | Link between picking and sale order
[stock_picking_send_by_mail](stock_picking_send_by_mail/) | 14.0.1.0.0 |  | Send stock picking by email
[stock_picking_show_backorder](stock_picking_show_backorder/) | 14.0.1.0.0 |  | Provides a new field on stock pickings, allowing to display the corresponding backorders.
[stock_picking_show_return](stock_picking_show_return/) | 14.0.1.0.1 |  | Show returns on stock pickings
[stock_picking_supplier_ref](stock_picking_supplier_ref/) | 14.0.1.1.1 |  | Adds a supplier reference field inside supplier's pickings and allows search for this reference.
[stock_picking_tier_validation](stock_picking_tier_validation/) | 14.0.1.0.1 |  | Extends the functionality of Transfers to support a tier validation process.
[stock_picking_warn_message](stock_picking_warn_message/) | 14.0.2.0.0 |  | Add a popup warning on picking to ensure warning is populated
[stock_production_lot_active](stock_production_lot_active/) | 14.0.1.0.1 | [![ThomasBinsfeld](https://github.com/ThomasBinsfeld.png?size=30px)](https://github.com/ThomasBinsfeld) | Allow to archive/unarchive a lot.
[stock_push_delay](stock_push_delay/) | 14.0.1.0.1 |  | Manual evaluation of Push rules
[stock_putaway_by_route](stock_putaway_by_route/) | 14.0.1.0.0 |  | Add a match by route on putaway, after product and categories
[stock_putaway_hook](stock_putaway_hook/) | 14.0.1.0.0 |  | Add hooks allowing modules to add more putaway strategies
[stock_quant_package_dimension](stock_quant_package_dimension/) | 14.0.2.2.0 |  | Use dimensions on packages
[stock_quant_package_dimension_total_weight_from_packaging](stock_quant_package_dimension_total_weight_from_packaging/) | 14.0.1.1.0 |  | Estimated weight of a package
[stock_quant_package_product_packaging](stock_quant_package_product_packaging/) | 14.0.1.1.0 |  | Use product packagings on packages
[stock_restrict_lot](stock_restrict_lot/) | 14.0.1.3.0 | [![florian-dacosta](https://github.com/florian-dacosta.png?size=30px)](https://github.com/florian-dacosta) | Base module that add back the concept of restrict lot on stock move
[stock_restrict_lot_update](stock_restrict_lot_update/) | 14.0.1.0.0 | [![aleuffre](https://github.com/aleuffre.png?size=30px)](https://github.com/aleuffre) [![renda-dev](https://github.com/renda-dev.png?size=30px)](https://github.com/renda-dev) | Only apply lot restriction on products in a domain
[stock_return_request](stock_return_request/) | 14.0.1.0.3 |  | Stock Return Request
[stock_scheduler_assignation_horizon](stock_scheduler_assignation_horizon/) | 14.0.1.1.0 |  | Set a timeframe limit to the delivery scheduler
[stock_split_picking](stock_split_picking/) | 14.0.1.1.2 |  | Split a picking in two not transferred pickings
[stock_valuation_layer_by_category](stock_valuation_layer_by_category/) | 14.0.1.0.0 |  | Display stock valuation layer by category
[stock_valuation_layer_usage](stock_valuation_layer_usage/) | 14.0.1.0.1 |  | Trace where has the stock valuation been used in, including the quantities taken.
[stock_valuation_no_developer_mode](stock_valuation_no_developer_mode/) | 14.0.1.0.1 |  | Stock valuation layer no developer mode

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
