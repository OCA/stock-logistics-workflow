Odoo works out the average cost of a product from its stock valuation layers,
and never restates one once it is written: a correction is always booked as a
new layer, dated the day it is made, and everything that was valued in between
keeps the figures it was given. That is a sound rule when the stock valuation is
posted movement by movement, and it is exactly what falls short when it is not.

This module restates the layer instead. When the cost or the quantity of an
already validated valuation layer is corrected, the layer is rewritten as if it
had always held the corrected figures, and the whole chain is replayed from
there on. That is what it buys:

- **A mistake made on a receipt can really be undone.** Somebody types the price
  of a purchase wrong, or enters the quantity in the wrong unit, and it is only
  noticed days later. Correcting the receipt is enough: the layer, the cost of
  the product and everything valued afterwards line up with what actually
  happened.

- **The outgoing moves valued in between are re-priced.** The units that left
  stock while the mistake was in place had been valued with the wrong average.
  They are given the cost they should have had, so the cost of goods sold stops
  carrying the error, and anything that reads the cost of an outgoing layer
  follows along. The margin `sale_margin_sync` writes on the sale order line is
  one such reader.

- **A stock valuation asked for a past date comes out corrected.** The valuation
  report adds up the current value of the layers created up to the requested
  date, so restating them is what makes a valuation as of last month right once
  a mistake made last month is fixed this one. Where the stock valuation is
  posted periodically rather than movement by movement, this is what allows the
  period to be closed with corrected figures instead of dragging the error into
  the next one.

- **The cost of an oversold product or lot doesn't run away.** With no units
  left to average against, Odoo still weighs the incoming cost against the
  negative quantity, and dividing by it returns a price that is not an average
  of anything and that can even be negative, which every outgoing move then
  copies. Here the cost of the receipt becomes the new average, which is also
  the cost Odoo's own negative stock vacuum uses to settle the deficit once
  enough real stock arrives, so both ends agree and the cost is always a price
  that was really paid.

- **Products valuated by lot are supported.** Each lot is replayed as its own
  chain, so a correction only re-prices what left that very lot and the other
  lots keep their own cost. Products valuated as a whole and products valuated
  by lot can coexist, and a product can be switched from one to the other at any
  time.
