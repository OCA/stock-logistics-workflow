By default, the automatic package creation logic may generate a unique package for every single unit of a product if
no specific packaging is defined on the product template. This can lead to the accidental creation of hundreds
of unnecessary package records upon picking validation.

This module adds a new field, auto_pack_requires_packaging, to the Operation Types.
When this option is enabled, the automatic packaging process will skip any products
that do not have packaging defined, preventing the accidental generation of
single-unit packages.
