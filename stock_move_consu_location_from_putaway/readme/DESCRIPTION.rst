This module allows, for consumable products, to use the putaway location
as a source location of the stock move line, when the stock move
use a parent location of the putaway location as its source location.

As Odoo allows to define putaway rules for consumable products, incoming moves
will have the putaway applied to define the destination location of the
move lines, allowing to display this location in the Picking Operations report.

On outgoing moves though, as the stock levels are obviously not managed for
consumable products, there is no quantity to reserve in any location and the
Picking Operations report can only display the source location of the move.

With this module however, as the location of the putaway will be used as
the source location of the move line, the Picking Operations report will
display this location where the consumable product is supposed to be stored.
