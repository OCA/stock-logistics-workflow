To configure this module you need to:

1.  Make sure to select the consignment option in inventory settings by
    going to *Inventory \> Configuration \> Settings* and ticking
    *Consignment* under *Traceability*.
2.  Go to *Inventory \> Configuration \> Operation Types*.
3.  Select an operation type, or create a new one, and set *Owner
    Restriction* field to the desired value.

Developers notes

This module update the context dependency of product quantity available
to be computed correctly. If you need get product quantity available for
an owner yo need set the context key "force_restricted_owner_id".
