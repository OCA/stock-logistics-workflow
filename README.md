
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
[delivery_procurement_group_carrier](delivery_procurement_group_carrier/) | 18.0.1.0.0 |  | Delivery Procurement Group Carrier
[procurement_auto_create_group_carrier](procurement_auto_create_group_carrier/) | 18.0.1.0.0 |  | Procurement Auto Create Group Carrier
[product_cost_price_avco_sync](product_cost_price_avco_sync/) | 18.0.1.0.0 | [![carlosdauden](https://github.com/carlosdauden.png?size=30px)](https://github.com/carlosdauden) [![sergio-teruel](https://github.com/sergio-teruel.png?size=30px)](https://github.com/sergio-teruel) | Set product cost price from updated moves
[purchase_stock_picking_invoice_link](purchase_stock_picking_invoice_link/) | 18.0.1.0.0 |  | Adds link between purchases, pickings and invoices
[sale_order_global_stock_route](sale_order_global_stock_route/) | 18.0.1.0.0 |  | Add the possibility to choose one warehouse path for an order
[stock_account_product_run_fifo_hook](stock_account_product_run_fifo_hook/) | 18.0.1.0.1 |  | Add more flexibility in the run fifo method.
[stock_dangerous_goods](stock_dangerous_goods/) | 18.0.1.0.0 | [![mmequignon](https://github.com/mmequignon.png?size=30px)](https://github.com/mmequignon) | Adds utility fields to manage dangerous goods
[stock_landed_costs_priority](stock_landed_costs_priority/) | 18.0.1.0.0 |  | Add priority to landed costs
[stock_lock_lot](stock_lock_lot/) | 18.0.1.0.0 |  | Stock Lock Lot
[stock_move_quantity_product_uom](stock_move_quantity_product_uom/) | 18.0.1.0.2 |  | computes stock.move's quantity in the uom of the product.
[stock_no_negative](stock_no_negative/) | 18.0.1.0.2 |  | Disallow negative stock levels by default
[stock_owner_restriction](stock_owner_restriction/) | 18.0.1.0.0 |  | Do not reserve quantity with assigned owner
[stock_partner_delivery_window](stock_partner_delivery_window/) | 18.0.1.0.0 |  | Define preferred delivery time windows for partners
[stock_picking_auto_create_lot](stock_picking_auto_create_lot/) | 18.0.1.0.0 | [![sergio-teruel](https://github.com/sergio-teruel.png?size=30px)](https://github.com/sergio-teruel) | Auto create lots for incoming pickings
[stock_picking_back2draft](stock_picking_back2draft/) | 18.0.1.0.0 |  | Reopen canceled transfers
[stock_picking_backorder_strategy_cancel](stock_picking_backorder_strategy_cancel/) | 18.0.1.0.0 | [![rousseldenis](https://github.com/rousseldenis.png?size=30px)](https://github.com/rousseldenis) [![mgosai](https://github.com/mgosai.png?size=30px)](https://github.com/mgosai) | Picking backordering strategies
[stock_picking_batch_invoice_frequency](stock_picking_batch_invoice_frequency/) | 18.0.1.0.1 | [![EmilioPascual](https://github.com/EmilioPascual.png?size=30px)](https://github.com/EmilioPascual) [![rafaelbn](https://github.com/rafaelbn.png?size=30px)](https://github.com/rafaelbn) | Invoice Sale Orders from Stock Pickin Batch
[stock_picking_filter_lot](stock_picking_filter_lot/) | 18.0.1.0.0 |  | In picking out lots' selection, filter lots based on their location
[stock_picking_group_by_base](stock_picking_group_by_base/) | 18.0.1.0.0 |  | Allows to define a way to create index on extensible domain
[stock_picking_invoice_link](stock_picking_invoice_link/) | 18.0.1.0.0 |  | Adds link between pickings and invoices
[stock_picking_kind](stock_picking_kind/) | 18.0.1.0.0 |  | Computes the kind of picking based on locations
[stock_picking_origin_reference](stock_picking_origin_reference/) | 18.0.1.0.0 |  | Add clickable button to the Transfer Source Document.
[stock_picking_partner_note](stock_picking_partner_note/) | 18.0.1.0.0 |  | Add partner notes on picking
[stock_picking_progress](stock_picking_progress/) | 18.0.1.0.0 | [![mmequignon](https://github.com/mmequignon.png?size=30px)](https://github.com/mmequignon) [![JuMiSanAr](https://github.com/JuMiSanAr.png?size=30px)](https://github.com/JuMiSanAr) | Compute the stock.picking progression
[stock_picking_purchase_order_link](stock_picking_purchase_order_link/) | 18.0.1.0.0 |  | Link between picking and purchase order
[stock_picking_restrict_cancel_printed](stock_picking_restrict_cancel_printed/) | 18.0.1.0.0 | [![jbaudoux](https://github.com/jbaudoux.png?size=30px)](https://github.com/jbaudoux) | Prevent canceling a stock transfer if printed.
[stock_picking_return_restricted_qty](stock_picking_return_restricted_qty/) | 18.0.1.0.0 |  | Restrict the return to delivered quantity
[stock_picking_sale_order_link](stock_picking_sale_order_link/) | 18.0.1.0.0 |  | Link between picking and sale order
[stock_picking_send_by_mail](stock_picking_send_by_mail/) | 18.0.1.0.0 |  | Send stock picking by email
[stock_picking_show_backorder](stock_picking_show_backorder/) | 18.0.1.0.0 |  | Provides a new field on stock pickings, allowing to display the corresponding backorders.
[stock_picking_show_return](stock_picking_show_return/) | 18.0.1.0.0 |  | Show returns on stock pickings
[stock_picking_type_force_move_type](stock_picking_type_force_move_type/) | 18.0.1.0.0 |  | Force shipping policies on operation types
[stock_picking_warn_message](stock_picking_warn_message/) | 18.0.1.0.0 |  | Add a popup warning on picking to ensure warning is populated
[stock_picking_whole_scrap](stock_picking_whole_scrap/) | 18.0.1.0.0 | [![sergio-teruel](https://github.com/sergio-teruel.png?size=30px)](https://github.com/sergio-teruel) | Create whole scrap from a picking for move lines
[stock_product_set](stock_product_set/) | 18.0.1.0.0 | [![victoralmau](https://github.com/victoralmau.png?size=30px)](https://github.com/victoralmau) | Add product sets in pickings
[stock_restrict_lot](stock_restrict_lot/) | 18.0.1.0.0 | [![florian-dacosta](https://github.com/florian-dacosta.png?size=30px)](https://github.com/florian-dacosta) | Base module that add back the concept of restrict lot on stock move
[stock_split_picking](stock_split_picking/) | 18.0.1.0.0 |  | Split a picking in two not transferred pickings
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
