In multi-step deliveries that use pull rules, validating an upstream picking
with a quantity different from the initial demand does not automatically
propagate that variance to the next delivery step.

As a result, the downstream moves can keep the original demanded quantity even
though the previous operation was completed with a lower or higher actual
quantity.

This module keeps the sale flow aligned by updating the related sale order line,
so the following pull-generated moves are recomputed with the processed
quantity.
