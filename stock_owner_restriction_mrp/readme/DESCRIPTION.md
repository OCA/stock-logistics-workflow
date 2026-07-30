Bridge between `stock_owner_restriction` and `mrp`, so manufacturing follows the
owner restriction the same way pickings do.

It fixes an asymmetry that silently destroys the valuation of manufactured
products. Odoo declines to value the consumption of goods that belong to a
partner — fair enough, they are not yours — and then values the finished product
anyway, at whatever the components cost, which by then is nothing. Every such
order books stock out of thin air: the average cost of the product collapses,
and so does the cost of everything made from it afterwards.

Naming the owner on the way out stops it at the source: what is made out of
somebody else's goods belongs to them too, so the move produces no valuation
layer at all rather than a zero-cost one.

It also gives the raw material of a manufacturing order a partner to be
restricted to, which it did not have.
