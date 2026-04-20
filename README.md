
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/stock-logistics-workflow&target_branch=19.0)
[![Pre-commit Status](https://github.com/OCA/stock-logistics-workflow/actions/workflows/pre-commit.yml/badge.svg?branch=19.0)](https://github.com/OCA/stock-logistics-workflow/actions/workflows/pre-commit.yml?query=branch%3A19.0)
[![Build Status](https://github.com/OCA/stock-logistics-workflow/actions/workflows/test.yml/badge.svg?branch=19.0)](https://github.com/OCA/stock-logistics-workflow/actions/workflows/test.yml?query=branch%3A19.0)
[![codecov](https://codecov.io/gh/OCA/stock-logistics-workflow/branch/19.0/graph/badge.svg)](https://codecov.io/gh/OCA/stock-logistics-workflow)
[![Translation Status](https://translation.odoo-community.org/widgets/stock-logistics-workflow-19-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/stock-logistics-workflow-19-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# Stock Workflow

Enhance the way flows and processes are working. Find here modules that do not have their place in the other more specialized repositories.

Are you looking for modules related to logistics? Or would like to contribute
to? There are many repositories with specific purposes. Have a look at this
[README](https://github.com/OCA/wms/blob/19.0/README.md).

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[sale_stock_picking_invoice_link](sale_stock_picking_invoice_link/) | 19.0.1.0.0 |  | Adds link between pickings and invoices
[stock_dangerous_goods](stock_dangerous_goods/) | 19.0.1.0.0 | <a href='https://github.com/mmequignon'><img src='https://github.com/mmequignon.png' width='32' height='32' style='border-radius:50%;' alt='mmequignon'/></a> | Adds utility fields to manage dangerous goods
[stock_lot_scrap](stock_lot_scrap/) | 19.0.1.0.0 |  | This module adds a button in Production Lot/Serial Number view form to Scrap all products contained.
[stock_no_negative](stock_no_negative/) | 19.0.1.0.0 |  | Disallow negative stock levels by default
[stock_picking_auto_create_lot](stock_picking_auto_create_lot/) | 19.0.1.0.0 | <a href='https://github.com/sergio-teruel'><img src='https://github.com/sergio-teruel.png' width='32' height='32' style='border-radius:50%;' alt='sergio-teruel'/></a> | Auto create lots for incoming pickings
[stock_picking_auto_create_package](stock_picking_auto_create_package/) | 19.0.1.0.0 |  | Put all move lines in packs on validation.
[stock_picking_back2draft](stock_picking_back2draft/) | 19.0.1.0.0 |  | Reopen canceled transfers
[stock_picking_batch_partner_enable](stock_picking_batch_partner_enable/) | 19.0.1.0.0 | <a href='https://github.com/ivantodorovich'><img src='https://github.com/ivantodorovich.png' width='32' height='32' style='border-radius:50%;' alt='ivantodorovich'/></a> | Control the Automatic Batches grouping per partner
[stock_picking_batch_substate](stock_picking_batch_substate/) | 19.0.1.0.0 |  | Batch Transfer Sub State
[stock_picking_filter_lot](stock_picking_filter_lot/) | 19.0.1.0.0 |  | In picking out lots' selection, filter lots based on their location
[stock_picking_invoice_link](stock_picking_invoice_link/) | 19.0.1.0.1 |  | Adds link between pickings and invoices
[stock_picking_kind](stock_picking_kind/) | 19.0.1.0.0 |  | Computes the kind of picking based on locations
[stock_picking_origin_reference](stock_picking_origin_reference/) | 19.0.1.0.0 |  | Add clickable button to the Transfer Source Document.
[stock_picking_purchase_order_link](stock_picking_purchase_order_link/) | 19.0.1.0.0 |  | Link between picking and purchase order
[stock_picking_return_restricted_qty](stock_picking_return_restricted_qty/) | 19.0.1.0.0 |  | Restrict the return to delivered quantity
[stock_picking_sale_order_link](stock_picking_sale_order_link/) | 19.0.1.0.0 |  | Link between picking and sale order
[stock_picking_send_by_mail](stock_picking_send_by_mail/) | 19.0.1.0.0 |  | Send stock picking by email
[stock_split_picking](stock_split_picking/) | 19.0.1.0.0 |  | Split a picking in two not transferred pickings

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
