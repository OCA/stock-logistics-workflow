This module adds a Shipment Composer document to compose a shipment out of stock moves
that belong to different transfers. It is useful when you need to aggregate stock moves
from multiple deliveries into one shipment, or to ship a single transfer in several
shipments.

A composer collects moves sharing the same partner and operation type, one line per
move with its own quantity, so a move can be shipped partially and the rest allocated to
another composer. You reserve stock and validate from the composer, which processes only
the composed quantities and blocks direct validation of the transfers involved.
