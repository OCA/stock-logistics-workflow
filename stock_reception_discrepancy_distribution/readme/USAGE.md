## One-time setup

1.  *Inventory > Configuration > Settings*: tick **Multi-Step Routes**
    and save.
2.  *Inventory > Configuration > Warehouse Management > Routes*: in the
    search bar open **Filters** and tick **Archived**, then open
    **Replenish on Order (MTO)** and unarchive it.
3.  Open a storable product (*Inventory > Products > Products*):
    -   **Product Type**: *Goods*, with **Track Inventory** ticked.
    -   **Inventory** tab → *Operations*: tick **Buy** and
        **Replenish on Order (MTO)**.
    -   **Purchase** tab: add a vendor with a price.

## Flow

1.  *Sales > Orders > Quotations*: create one quotation for **Customer
    A** with the product, quantity 10, and confirm it.
2.  Create a second quotation for **Customer B**, quantity 15, and
    confirm it.
3.  *Purchase > Orders > Requests for Quotation*: open the RFQ that
    has been auto-created (one line, 25 units) and click
    **Confirm Order**.
4.  On the purchase order, click **Receive Products**.
5.  In the **Operations** tab of the receipt, raise **Quantity** to
    `30` and tick **Picked**.
6.  Next to **Quantity**, click the small fork icon (tooltip
    *Change qty on dest moves*). The wizard opens.
7.  In the wizard the header shows *Quantity = 30*,
    *Move Dest Demand = 25*, *Over Quantity = 5*. Under
    **Destination stock moves** edit **Demand** on each line so the
    total matches 30 (e.g. `12` and `18`). The header turns green
    when both numbers are equal.
8.  Click **Confirm**, then **Validate** the receipt.

### Expected result

-   The receipt is *Done* and **no backorder** is created.
-   Each customer's outgoing transfer has the redistributed demand
    (12 and 18 in the example).

The button stays hidden on transfers that are *Done* / *Cancelled*,
on non-incoming transfers, and on return moves.
