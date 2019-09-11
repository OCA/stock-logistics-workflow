11.0.1.0.0 (2018-12-06)
~~~~~~~~~~~~~~~~~~~~~~~

* [11.0][MIG] stock_picking_backorder_strategy
  Migration to v11.0
  Field pack_operation_ids removed in v11
  Method do_new_transfer changed to button_validate

10.0.1.0.0 (2018-06-06)
~~~~~~~~~~~~~~~~~~~~~~~

* [10.0][MIG] stock_picking_backorder_strategy
  Migration to v10.0
  Added a default 'manual' strategy according to changed flow in pickings.
  Let the normal process (backorder wizard) occurs

8.0.1.0.0 (2015-08-13)
~~~~~~~~~~~~~~~~~~~~~~~

* [ADD] add module stock_backorder_strategy
  Define on stock_picking_type how to manage backorder.
  create: default behavior
  no_create: no backorder created
  cancel: backorder is cancelled
