This module extends the functionality of stock module to allow
restriction of product quantities (quants) for stock operations such as
reserve quantities or product quantity available info.

It also propagates the restrict partner (owner) of a procurement to the
stock moves and through chained moves (pull and push rules). Moves with a
different restrict partner are not grouped into the same picking and the
restrict partner is set as owner on the pickings.
