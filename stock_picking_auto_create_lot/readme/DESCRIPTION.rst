This module extends the functionality of stock module to allow auto create
lots for incoming pickings.

The lot names are generated from a configurable expression that uses the
inline template syntax. It is configured in on the operation type
(``stock.picking.type``) (Lot Name Expression field).

The expression has access to some default variables provided by inline
templates (like ``datetime``), as well as the product move (stock move line)
as ``stock_move_line``.

If empty, the default value for lot names is used.

Here is an example of an expression that uses the supplier's name and the
date (this will result in the same lot being used for multiple stock moves):

.. code-block::

    {{stock_move_line.picking_id.partner_id.name}}/{{datetime.date.today().isoformat()}}

Here is an example using the default sequence directly:

.. code-block::

    {{stock_move_line.env["ir.sequence"].next_by_code("stock.lot.serial")}}
