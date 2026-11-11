This module adds a Removal Date field to stock valuation layers, taken from the
lots/serials of the related stock move.

The standard Lot/Serial Number field of a valuation layer is only filled for
products with lot valuation enabled, so the lots are read from the stock move
instead, which works regardless of that setting. When the move holds several
lots, the earliest removal date of those lots is kept.

The field is stored and indexed, so that the valuation layers can be filtered,
sorted and grouped by removal date. Existing layers are filled in SQL by a
pre-install hook rather than by the ORM, which keeps the installation of the
module fast even on databases holding a large number of valuation layers.
