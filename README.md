
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/stock-logistics-workflow&target_branch=14.0)
[![Build Status](https://travis-ci.com/OCA/stock-logistics-workflow.svg?branch=14.0)](https://travis-ci.com/OCA/stock-logistics-workflow)
[![codecov](https://codecov.io/gh/OCA/stock-logistics-workflow/branch/14.0/graph/badge.svg)](https://codecov.io/gh/OCA/stock-logistics-workflow)
[![Translation Status](https://translation.odoo-community.org/widgets/stock-logistics-workflow-14-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/stock-logistics-workflow-14-0/?utm_source=widget)

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
[delivery_package_default_shipping_weight](delivery_package_default_shipping_weight/) | 14.0.1.0.1 |  | Set default package shipping weight according to packaging
[delivery_procurement_group_carrier](delivery_procurement_group_carrier/) | 14.0.1.1.0 |  | Delivery Procurement Group Carrier
[delivery_total_weight_from_packaging](delivery_total_weight_from_packaging/) | 14.0.1.0.0 |  | Include packaging weight on move, transfer and package.
[procurement_auto_create_group_carrier](procurement_auto_create_group_carrier/) | 14.0.1.1.0 |  | Procurement Auto Create Group Carrier
[product_supplierinfo_for_customer_picking](product_supplierinfo_for_customer_picking/) | 14.0.1.0.1 |  | This module makes the product customer code visible in the stock moves of a picking.
[sale_stock_mto_as_mts_orderpoint](sale_stock_mto_as_mts_orderpoint/) | 14.0.1.0.1 |  | Materialize need from MTO route through orderpoint
[stock_auto_move](stock_auto_move/) | 14.0.1.0.0 |  | Automatic Move Processing
[stock_delivery_note](stock_delivery_note/) | 14.0.1.0.1 |  | This module allows to fill in a delivery note that will be displayed on delivery report
[stock_lock_lot](stock_lock_lot/) | 14.0.1.0.0 |  | Stock Lock Lot
[stock_move_assign_picking_hook](stock_move_assign_picking_hook/) | 14.0.1.1.1 |  | Stock Move picking assignment hook
[stock_move_change_source_location](stock_move_change_source_location/) | 14.0.1.0.0 |  | This module allows you to change the source location of a stock move from the picking
[stock_move_line_auto_fill](stock_move_line_auto_fill/) | 14.0.1.0.0 |  | Stock Move Line auto fill
[stock_no_negative](stock_no_negative/) | 14.0.1.0.1 |  | Disallow negative stock levels by default
[stock_owner_restriction](stock_owner_restriction/) | 14.0.1.0.1 |  | Do not reserve quantity with assigned owner
[stock_partner_delivery_window](stock_partner_delivery_window/) | 14.0.1.2.0 |  | Define preferred delivery time windows for partners
[stock_picking_auto_create_lot](stock_picking_auto_create_lot/) | 14.0.1.0.0 | [![sergio-teruel](https://github.com/sergio-teruel.png?size=30px)](https://github.com/sergio-teruel) | Auto create lots for incoming pickings
[stock_picking_back2draft](stock_picking_back2draft/) | 14.0.1.0.0 |  | Reopen cancelled pickings
[stock_picking_backorder_strategy](stock_picking_backorder_strategy/) | 14.0.1.0.0 | [![rousseldenis](https://github.com/rousseldenis.png?size=30px)](https://github.com/rousseldenis) [![mgosai](https://github.com/mgosai.png?size=30px)](https://github.com/mgosai) | Picking backordering strategies
[stock_picking_batch_extended](stock_picking_batch_extended/) | 14.0.1.0.0 | [![gurneyalex](https://github.com/gurneyalex.png?size=30px)](https://github.com/gurneyalex) [![carlosdauden](https://github.com/carlosdauden.png?size=30px)](https://github.com/carlosdauden) [![i-vyshnevska](https://github.com/i-vyshnevska.png?size=30px)](https://github.com/i-vyshnevska) | Allows manage a lot of pickings in batch
[stock_picking_cancel_reason](stock_picking_cancel_reason/) | 14.0.1.0.0 |  | Stock Picking Cancel Reason
[stock_picking_filter_lot](stock_picking_filter_lot/) | 14.0.1.0.1 |  | In picking out lots' selection, filter lots based on their location
[stock_picking_group_by_partner_by_carrier](stock_picking_group_by_partner_by_carrier/) | 14.0.1.4.2 |  | Stock Picking: group by partner and carrier
[stock_picking_group_by_partner_by_carrier_by_date](stock_picking_group_by_partner_by_carrier_by_date/) | 14.0.1.0.1 |  | Stock Picking: group by partner and carrier and scheduled date
[stock_picking_invoice_link](stock_picking_invoice_link/) | 14.0.1.1.1 |  | Adds link between pickings and invoices
[stock_picking_line_sequence](stock_picking_line_sequence/) | 14.0.1.0.0 |  | Manages the order of stock moves by displaying its sequence
[stock_picking_mass_action](stock_picking_mass_action/) | 14.0.1.0.1 |  | Stock Picking Mass Action
[stock_picking_purchase_order_link](stock_picking_purchase_order_link/) | 14.0.1.0.1 |  | Link between picking and purchase order
[stock_picking_restrict_cancel_with_orig_move](stock_picking_restrict_cancel_with_orig_move/) | 14.0.1.0.1 |  | Restrict cancellation of dest moves according to origin.
[stock_picking_sale_order_link](stock_picking_sale_order_link/) | 14.0.1.0.1 |  | Link between picking and sale order
[stock_picking_send_by_mail](stock_picking_send_by_mail/) | 14.0.1.0.0 |  | Send stock picking by email
[stock_picking_show_backorder](stock_picking_show_backorder/) | 14.0.1.0.0 |  | Provides a new field on stock pickings, allowing to display the corresponding backorders.
[stock_picking_show_return](stock_picking_show_return/) | 14.0.1.0.1 |  | Show returns on stock pickings
[stock_picking_warn_message](stock_picking_warn_message/) | 14.0.1.0.1 |  | Add a popup warning on picking to ensure warning is populated
[stock_production_lot_active](stock_production_lot_active/) | 14.0.1.0.0 | [![ThomasBinsfeld](https://github.com/ThomasBinsfeld.png?size=30px)](https://github.com/ThomasBinsfeld) | Allow to archive/unarchive a lot.
[stock_push_delay](stock_push_delay/) | 14.0.1.0.1 |  | Manual evaluation of Push rules
[stock_putaway_by_route](stock_putaway_by_route/) | 14.0.1.0.0 |  | Add a match by route on putaway, after product and categories
[stock_putaway_hook](stock_putaway_hook/) | 14.0.1.0.0 |  | Add hooks allowing modules to add more putaway strategies
[stock_quant_package_dimension](stock_quant_package_dimension/) | 14.0.2.2.0 |  | Use dimensions on packages
[stock_quant_package_dimension_total_weight_from_packaging](stock_quant_package_dimension_total_weight_from_packaging/) | 14.0.1.1.0 |  | Estimated weight of a package
[stock_quant_package_product_packaging](stock_quant_package_product_packaging/) | 14.0.1.1.0 |  | Use product packagings on packages
[stock_restrict_lot](stock_restrict_lot/) | 14.0.1.1.1 | [![florian-dacosta](https://github.com/florian-dacosta.png?size=30px)](https://github.com/florian-dacosta) | Base module that add back the concept of restrict lot on stock move
[stock_return_request](stock_return_request/) | 14.0.1.0.2 |  | Stock Return Request
[stock_split_picking](stock_split_picking/) | 14.0.1.1.0 |  | Split a picking in two not transferred pickings
[stock_valuation_layer_by_category](stock_valuation_layer_by_category/) | 14.0.1.0.0 |  | Display stock valuation layer by category
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
