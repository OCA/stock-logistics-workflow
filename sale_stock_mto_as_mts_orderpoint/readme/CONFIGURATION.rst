On the original MTO route, you have two options to configure the rule to pull
from Stock:

* Keep the triggering of another rule as Supply Method on stock.rule, will
  ensure that the need is materialized by the procure_recommended_qty on the
  orderpoint, if the ensuing procurement (purchase order/manufacturing order)
  having the MTO rule as origin is canceled.

* Change the Supply Method on stock.rule to Take From Stock, will ensure that
  the need is materialized by the procure_recommended_qty on the orderpoint,
  if the ensuing procurement (purchase order/manufacturing order) having the
  orderpoint as origin is canceled.
