Companies handling perishable goods need to know how much of their stock value
is about to expire, and how much of the value they consumed came from stock
that was close to its removal date. Odoo stores the removal date of a lot on
the quants of that lot (`product_expiry`), which shows the exposure of the
stock on hand, but the valuation layers keep no trace of it once the goods have
moved.

Reaching the removal date from a valuation layer means walking through the
stock move and its move lines up to the lots, which is impractical for
filtering and impossible to group by. Storing the date on the layer makes the
valuation report answer those questions directly.
