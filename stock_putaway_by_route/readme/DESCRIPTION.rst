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

Note: it is based on the Stock Rule stored on a move, so it cannot be applied
on a route without rule.
