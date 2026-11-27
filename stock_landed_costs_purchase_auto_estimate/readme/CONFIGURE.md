Optionally, set an *Estimated Landed Cost Product* under
*Inventory > Configuration > Settings > Landed Costs* (a service product
flagged *Is a Landed Cost*, typically with a freight expense account).

When set, each automatically created estimate carries a single cost line on
that product, and the landed-cost entry debits the goods' stock valuation
account and credits the product's expense account — the same account the
actual freight invoice debits later, so its balance is the
estimate-vs-actual variance.

When empty, each estimate line keeps the purchased product and both legs of
the entry hit the stock valuation account.
