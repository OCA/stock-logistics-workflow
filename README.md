
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/stock-logistics-workflow&target_branch=17.0)
[![Pre-commit Status](https://github.com/OCA/stock-logistics-workflow/actions/workflows/pre-commit.yml/badge.svg?branch=17.0)](https://github.com/OCA/stock-logistics-workflow/actions/workflows/pre-commit.yml?query=branch%3A17.0)
[![Build Status](https://github.com/OCA/stock-logistics-workflow/actions/workflows/test.yml/badge.svg?branch=17.0)](https://github.com/OCA/stock-logistics-workflow/actions/workflows/test.yml?query=branch%3A17.0)
[![codecov](https://codecov.io/gh/OCA/stock-logistics-workflow/branch/17.0/graph/badge.svg)](https://codecov.io/gh/OCA/stock-logistics-workflow)
[![Translation Status](https://translation.odoo-community.org/widgets/stock-logistics-workflow-17-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/stock-logistics-workflow-17-0/?utm_source=widget)

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
[delivery_procurement_group_carrier](delivery_procurement_group_carrier/) | 17.0.1.1.1 |  | Delivery Procurement Group Carrier
[product_cost_price_avco_sync](product_cost_price_avco_sync/) | 17.0.1.0.0 | <a href='https://github.com/carlosdauden'><img src='https://github.com/carlosdauden.png' width='32' height='32' style='border-radius:50%;' alt='carlosdauden'/></a> <a href='https://github.com/sergio-teruel'><img src='https://github.com/sergio-teruel.png' width='32' height='32' style='border-radius:50%;' alt='sergio-teruel'/></a> | Set product cost price from updated moves
[purchase_stock_picking_invoice_link](purchase_stock_picking_invoice_link/) | 17.0.1.0.0 |  | Adds link between purchases, pickings and invoices
[sale_order_global_stock_route](sale_order_global_stock_route/) | 17.0.1.0.0 |  | Add the possibility to choose one warehouse path for an order
[sale_planned_consumed_date](sale_planned_consumed_date/) | 17.0.1.0.0 |  | Sale planned consumed date
[stock_account_product_run_fifo_hook](stock_account_product_run_fifo_hook/) | 17.0.1.0.1 |  | Add more flexibility in the run fifo method.
[stock_account_show_automatic_valuation](stock_account_show_automatic_valuation/) | 17.0.1.0.0 |  | Allow automatic valuation for stock moves in community edition
[stock_landed_costs_priority](stock_landed_costs_priority/) | 17.0.1.0.0 |  | Add priority to landed costs
[stock_lock_lot](stock_lock_lot/) | 17.0.1.0.0 |  | Stock Lock Lot
[stock_lot_on_hand_first](stock_lot_on_hand_first/) | 17.0.1.0.0 | <a href='https://github.com/grindtildeath'><img src='https://github.com/grindtildeath.png' width='32' height='32' style='border-radius:50%;' alt='grindtildeath'/></a> | Allows to display lots on hand first in M2o fields
[stock_lot_production_date](stock_lot_production_date/) | 17.0.1.0.0 | <a href='https://github.com/atchuthan'><img src='https://github.com/atchuthan.png' width='32' height='32' style='border-radius:50%;' alt='atchuthan'/></a> | Stock Lot Production Date
[stock_lot_scrap](stock_lot_scrap/) | 17.0.1.0.0 |  | This module adds a button in Production Lot/Serial Number view form to Scrap all products contained.
[stock_move_backdating](stock_move_backdating/) | 17.0.1.0.0 |  | Stock Move Backdating
[stock_move_forced_lot](stock_move_forced_lot/) | 17.0.1.0.0 |  | This module allows you to set a lot_id in a procurement to force the stock move generated to only reserve the selected lot.
[stock_move_line_reference_link](stock_move_line_reference_link/) | 17.0.1.0.0 |  | Add link in stock move line references.
[stock_move_planned_consumed_date](stock_move_planned_consumed_date/) | 17.0.1.0.0 |  | Stock Move planned consumed date
[stock_move_quantity_product_uom](stock_move_quantity_product_uom/) | 17.0.1.0.0 |  | computes stock.move's quantity in the uom of the product.
[stock_no_negative](stock_no_negative/) | 17.0.1.0.0 |  | Disallow negative stock levels by default
[stock_picking_auto_create_lot](stock_picking_auto_create_lot/) | 17.0.1.0.0 | <a href='https://github.com/sergio-teruel'><img src='https://github.com/sergio-teruel.png' width='32' height='32' style='border-radius:50%;' alt='sergio-teruel'/></a> | Auto create lots for incoming pickings
[stock_picking_auto_create_lot_sequence](stock_picking_auto_create_lot_sequence/) | 17.0.1.0.0 |  | Stock Picking Auto Create Lot Sequence
[stock_picking_back2draft](stock_picking_back2draft/) | 17.0.1.0.0 |  | Reopen cancelled pickings
[stock_picking_batch_print_pickings](stock_picking_batch_print_pickings/) | 17.0.1.0.0 | <a href='https://github.com/EmilioPascual'><img src='https://github.com/EmilioPascual.png' width='32' height='32' style='border-radius:50%;' alt='EmilioPascual'/></a> | Print Picking from Stock Picking Batch
[stock_picking_filter_lot](stock_picking_filter_lot/) | 17.0.1.0.0 |  | In picking out lots' selection, filter lots based on their location
[stock_picking_group_by_base](stock_picking_group_by_base/) | 17.0.1.0.1 |  | Allows to define a way to create index on extensible domain
[stock_picking_group_by_partner_by_carrier](stock_picking_group_by_partner_by_carrier/) | 17.0.0.0.0 |  | Stock Picking: group by partner and carrier
[stock_picking_invoice_link](stock_picking_invoice_link/) | 17.0.1.2.5 |  | Adds link between pickings and invoices
[stock_picking_kind](stock_picking_kind/) | 17.0.1.0.0 |  | Computes the kind of picking based on locations
[stock_picking_line_sequence](stock_picking_line_sequence/) | 17.0.1.0.1 |  | Manages the order of stock moves by displaying its sequence
[stock_picking_mass_action](stock_picking_mass_action/) | 17.0.1.0.0 |  | Stock Picking Mass Action
[stock_picking_origin_reference](stock_picking_origin_reference/) | 17.0.1.0.0 |  | Add clickable button to the Transfer Source Document.
[stock_picking_origin_reference_purchase](stock_picking_origin_reference_purchase/) | 17.0.1.0.0 |  | Transfer to Purchase Order navigation from the Source Document.
[stock_picking_origin_reference_sale](stock_picking_origin_reference_sale/) | 17.0.1.0.0 |  | Transfer to Sales Order navigation from the Source Document.
[stock_picking_partner_note](stock_picking_partner_note/) | 17.0.1.0.0 |  | Add partner notes on picking
[stock_picking_purchase_order_link](stock_picking_purchase_order_link/) | 17.0.1.0.0 |  | Link between picking and purchase order
[stock_picking_return_lot](stock_picking_return_lot/) | 17.0.1.0.0 |  | Propagate SN/lots from origin picking to return picking.
[stock_picking_return_restricted_qty](stock_picking_return_restricted_qty/) | 17.0.1.0.0 |  | Restrict the return to delivered quantity
[stock_picking_sale_order_link](stock_picking_sale_order_link/) | 17.0.1.0.0 |  | Link between picking and sale order
[stock_picking_send_by_mail](stock_picking_send_by_mail/) | 17.0.1.0.0 |  | Send stock picking by email
[stock_picking_show_backorder](stock_picking_show_backorder/) | 17.0.1.0.0 |  | Provides a new field on stock pickings, allowing to display the corresponding backorders.
[stock_picking_show_return](stock_picking_show_return/) | 17.0.1.0.1 |  | Show returns on stock pickings
[stock_picking_supplier_ref](stock_picking_supplier_ref/) | 17.0.1.0.0 |  | Adds a supplier reference field inside supplier's pickings and allows search for this reference.
[stock_picking_warn_message](stock_picking_warn_message/) | 17.0.1.0.0 |  | Add a popup warning on picking to ensure warning is populated
[stock_product_security](stock_product_security/) | 17.0.1.0.0 | <a href='https://github.com/peluko00'><img src='https://github.com/peluko00.png' width='32' height='32' style='border-radius:50%;' alt='peluko00'/></a> | Stock Product Security
[stock_production_lot_active](stock_production_lot_active/) | 17.0.1.0.0 | <a href='https://github.com/ThomasBinsfeld'><img src='https://github.com/ThomasBinsfeld.png' width='32' height='32' style='border-radius:50%;' alt='ThomasBinsfeld'/></a> | Allow to archive/unarchive lots/serial numbers
[stock_push_delay](stock_push_delay/) | 17.0.1.1.1 |  | Manual evaluation of Push rules
[stock_putaway_hook](stock_putaway_hook/) | 17.0.1.0.0 |  | Add hooks allowing modules to add more putaway strategies
[stock_quant_package_dimension](stock_quant_package_dimension/) | 17.0.1.0.0 |  | Use dimensions on packages
[stock_quant_package_product_packaging](stock_quant_package_product_packaging/) | 17.0.1.0.0 |  | Use product packagings on packages
[stock_restrict_by_planned_consumed_date](stock_restrict_by_planned_consumed_date/) | 17.0.1.0.0 |  | Stock restrict by planned consumed date
[stock_restrict_lot](stock_restrict_lot/) | 17.0.1.2.1 | <a href='https://github.com/florian-dacosta'><img src='https://github.com/florian-dacosta.png' width='32' height='32' style='border-radius:50%;' alt='florian-dacosta'/></a> | Base module that add back the concept of restrict lot on stock move
[stock_scrap_tier_validation](stock_scrap_tier_validation/) | 17.0.1.0.0 |  | Stock Scrap Tier Validation
[stock_scrap_tier_validation_mrp](stock_scrap_tier_validation_mrp/) | 17.0.1.0.0 |  | Stock Scrap Tier Validation: MRP compatibility
[stock_split_picking](stock_split_picking/) | 17.0.1.0.0 |  | Split a picking in two not transferred pickings
[stock_valuation_layer_usage](stock_valuation_layer_usage/) | 17.0.1.1.0 |  | Trace where has the stock valuation been used in, including the quantities taken.

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
