Nothing to configure in this module. It follows the *Owner Restriction* of the
manufacturing operation type, in *Inventory > Configuration > Operation Types*,
and does nothing while that is left as *Standard behavior*.

Once it is set to anything else:

1. The components of an order are reserved following that restriction. Where the
   order ends up delivering to a partner — its finished product chained to a
   delivery with an owner — that is the partner its components are taken from.
2. What comes out of an order made with a partner's goods is registered as
   belonging to that partner, and is therefore not valued.
3. An order cannot consume from more than one source. Mixing a partner's goods
   with the company's own, or two partners' goods, is refused when validating:
   there is no way to say that what came out belongs partly to each, so it has
   to be split into one order per owner.
