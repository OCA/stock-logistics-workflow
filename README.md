
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
[stock_no_negative](stock_no_negative/) | 15.0.1.0.0 |  | Disallow negative stock levels by default
[stock_picking_back2draft](stock_picking_back2draft/) | 15.0.1.0.1 |  | Reopen cancelled pickings
[stock_picking_filter_lot](stock_picking_filter_lot/) | 15.0.1.0.0 |  | In picking out lots' selection, filter lots based on their location
[stock_picking_info_lot](stock_picking_info_lot/) | 15.0.1.0.0 |  | Add lot information on Stock Transfer lines
[stock_picking_purchase_order_link](stock_picking_purchase_order_link/) | 15.0.1.0.0 |  | Link between picking and purchase order
[stock_picking_return_restricted_qty](stock_picking_return_restricted_qty/) | 15.0.1.0.0 |  | Restrict the return to delivered quantity
[stock_picking_sale_order_link](stock_picking_sale_order_link/) | 15.0.1.0.2 |  | Link between picking and sale order
[stock_picking_send_by_mail](stock_picking_send_by_mail/) | 15.0.1.0.0 |  | Send stock picking by email
[stock_picking_show_return](stock_picking_show_return/) | 15.0.1.0.0 |  | Show returns on stock pickings
[stock_picking_whole_scrap](stock_picking_whole_scrap/) | 15.0.1.0.0 | [![sergio-teruel](https://github.com/sergio-teruel.png?size=30px)](https://github.com/sergio-teruel) | Create whole scrap from a picking for move lines
[stock_production_lot_active](stock_production_lot_active/) | 15.0.1.0.2 | [![ThomasBinsfeld](https://github.com/ThomasBinsfeld.png?size=30px)](https://github.com/ThomasBinsfeld) | Allow to archive/unarchive a lot.
[stock_push_delay](stock_push_delay/) | 15.0.1.0.0 |  | Manual evaluation of Push rules
[stock_restrict_lot](stock_restrict_lot/) | 15.0.0.0.1 | [![florian-dacosta](https://github.com/florian-dacosta.png?size=30px)](https://github.com/florian-dacosta) | Base module that add back the concept of restrict lot on stock move
[stock_split_picking](stock_split_picking/) | 15.0.1.0.0 |  | Split a picking in two not transferred pickings

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
