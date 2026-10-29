To use this module you need to:

**To establish an owner to the merchandise you need to:**

1.  Go to *Inventory \> Overview*
2.  Create a incoming delivery order.
3.  Set an owner.

**The stock with owner assigned is not available in products:**

1.  Go to *Inventory \> Master Data \> Products*
2.  Search any product which is in incoming delivery order created in
    previos step.
3.  The quantity on hand has not take into account the incoming
    quanities with a owner assigned.

**Use cases:**

1.  *Odoo standard behavior.*

    > In picking operation type set "Standard behavior" value in "Owner
    > restriction" field.
    >
    > \*\* All product stock is available to delivery it.

2.  *Unassigned owner behavior.*

    > In picking operation type set "Unassigned owner" value in "Owner
    > restriction" field.
    >
    > \*\* Only product stock without owner assigned is available to
    > delivery it.

3.  *Picking partner behavior.*

    > In picking operation type set "Picking partner" value in "Owner
    > restriction" field.
    >
    > \*\* Only product stock with owner assigned is available to
    > delivery it.
    >
    > \*\* The owner is get from picking owner field or picking partner
    > field.
