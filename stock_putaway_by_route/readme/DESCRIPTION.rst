Add putaway rules based on a Stock Route.

The core putaway rules allow to select a putaway rule for: products, product categories.
This module adds the route.

For instance, a move generated for a replenishment (e.g. using the module
``Stock Orderpoint Route`` or ``Stock Buffer Route``) will be related to the
rule (so the route) that generated it. When the putaway rules are applied, if a
rule is defined on the replenishment route, the destination move will be changed
to the one of the rule.

The rules for the route are applied when no rule for product and categories have
been found.

When the put-away strategy by route is applied it looks:

1. If the move has a Stock Rule, it searches a put-away rule which has the
   same Rule's Route
2. Otherwise, if the Product has Route(s), it searches a put-away rule which
   has any Route of the product set (it takes the first found)
