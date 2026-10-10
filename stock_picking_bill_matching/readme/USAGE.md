# Usage

## Which scenario are you in?

| Your situation | What to read |
| --- | --- |
| The receipt is already validated (bill after the goods: an imported electronic invoice such as the Brazilian NFe, a portal invoice…) | 1 |
| The receipt exists but is still pending (goods on their way) | 1 |
| No purchase order, no receipt at all (small shop, imported bills, nothing encoded) | 2 |
| The document carries a line reference (in Brazil the NFe `xPed`/`nItemPed`, or one synthesized by the import wizard) | 5 |
| You want it to happen without any click | 2 and 5 (the *Auto-…* company settings) |

A single bill may need several of them: each line follows whichever applies.

## Demo data: play the scenarios

The module ships a small scenario (supplier **DEMO Supplier (bill matching)**,
created for it) that is built when the module is installed in a database **with
demo data** — the standard "create a new Odoo demo database" flow. It contains
two receipts and two bills:

| Record | What it is |
| --- | --- |
| receipt *DEMO-PO-1 (1st shipment)* | **Done**: 4 Acoustic Bloc Screens, already received |
| receipt *DEMO-PO-1 (2nd shipment)* | **Ready** (not received yet): 8 Acoustic Bloc Screens of the same order line |
| draft bill *DEMO - order DEMO-PO-1 (received + on its way)* | 4 + 6 Acoustic Bloc Screens, both carrying the reference `DEMO-PO-1`, plus a **section** line and a **service** line |
| draft bill *DEMO - nothing received yet (small shop flow)* | 12 Office Chairs, **no receipt and no purchase order** |

Both receipts and the two storable bill lines carry the matching reference
`DEMO-PO-1` (visible in the *Match Ref.* column of the matching screen). The
demo sets the `matching_reference` field directly; in a real database a
localization computes it instead (in Brazil, from the `xPed`/`nItemPed` fields
of the NFe, i.e. the purchase order and its line number).

### Scenario 1 — the bill arrives after the goods, one order line in two shipments

Open the *DEMO - order DEMO-PO-1* bill, click **Match Pickings**, then **Match
Selected** on the two storable lines (or select everything: the section and the
service line are ignored).

* the 4 units of the first shipment are **only linked**: the receipt is done, it
  is not touched, nothing is restocked (the everyday case);
* the 6 units still on their way are **received** by the matching, and the 2
  units the receipt had in excess become a **backorder**;
* the *Match Pickings* counter falls to 0, *Matched Items* shows 2, and the
  section/service lines were never counted as unmatched.

The two shipments share the same reference on purpose: a reference identifies
the **order line**, not the shipment (see the ordering note below).

### Scenario 2 — the same bill, matched automatically

Enable **Auto-Match Referenced Lines** (Inventory → Configuration → Settings →
Bill Matching), reopen the bill and click **Match Pickings** once: the
references do the pairing, with no selection at all. With **Auto-Match when
Posting the Bill** also enabled, this happens by itself when the bill is
posted.

### Scenario 3 — the small shop bill (nothing to match against)

Open the *DEMO - nothing received yet* bill: its lines have no receipt (and no
purchase order) to match with, so the matching screen is empty.

* **Create / Add to Picking** builds the receipt from those lines;
* or enable **Auto-Create the Receipt when Posting the Bill** (with
  **Auto-Validate Generated Pickings**) and simply **post** the bill: the
  receipt is created, linked to the bill and validated, with the bill as its
  origin and a chatter message linking back to it.

*Note: those transfers are prepared at installation time (the demo data is
built by the module's data files), so the scenario is complete in a fresh demo
database. In a database where the module was already installed before the demo
data was added, the demo records appear but their transfers stay in draft —
validate them by hand if you want to replay the scenario there.*

## 1. Matching Existing Pickings and Bills
Whether the warehouse already processed the receipt or not:
1. Open the Vendor Bill.
2. Click the **Match Pickings** smart button at the top right. The button shows
   how many lines of the bill still have to be matched.
3. You will be taken to the matching view.
4. Select the Vendor Bill line(s) and the corresponding Receipt line(s).
   * *Note: They are grouped by product, with Vendor Bills appearing above Receipts.
     Already validated receipts are listed too (their quantity is simply linked,
     nothing is re-validated).*
5. Click **Match Selected**.
   * The lines will vanish from the Unmatched view.
   * If the Receipt is *pending* and had a higher quantity, Odoo validates the
     matched quantity and creates a Backorder for the remaining quantity. If you
     later cancel the backorder and decide not to keep the extra stock, click
     **Force Matched** on the bill to settle it.
   * If the Receipt is *already validated*, it is only linked: the stock is
     untouched.
   * If the Bill had a higher quantity, the remaining billed quantity will stay
     in the view awaiting a future receipt, or you can create a new picking for
     it using the **Create / Add to Picking** button. If you decide the
     remaining quantity will never be delivered, you can click **Force Matched**
     to settle the bill anyway.

*Typical workflow:* Go to **Accounting -> Vendors -> Bills**, open the list view and apply the **Unmatched Picking** filter. This shows only vendor bills that still need to be matched. Work through them one by one — either by matching them against receipts in the matching view, or by forcing them to matched when the discrepancy is accepted. This keeps your todo list of bills to match clean and up to date.

## 2. "Small Shop" Replenishment (Auto-Create Pickings)
If you do not use Purchase Orders and simply import electronic Vendor Bills, you can generate your warehouse receipts in one click:
1. Open the Draft Vendor Bill.
2. Click the **Match Pickings** smart button.
3. In the matching view, select all vendor bill lines and click **Create / Add to Picking** in the header.
4. A wizard will appear. Leave the "Existing Picking" field blank.
5. Check the **Auto-Validate Receipt** checkbox if you want the stock to immediately enter your warehouse.
6. Click **Confirm**. The system will generate a `WH/IN` picking, populate it with all unmatched lines from the bill, and link them permanently.

*Tip: If the company setting **Auto-Create Picking on Match** is enabled, clicking **Match Pickings** on a bill with no open receipts will skip the matching view and generate the picking automatically.*

### Fully automatic: the receipt created when the bill is posted

With the **Auto-Create the Receipt when Posting the Bill** company setting (see
*Configuration*, and combine it with **Auto-Validate Generated Pickings** for
the stock to enter immediately), there is nothing left to click: importing an
electronic bill and validating it creates the receipt, links it and — if the
setting asks for it — validates it.

It is deliberately limited to the bills that have **nothing to match against**:
no purchase order for that vendor and no receipt candidate for the products
still to match. As soon as a document exists, matching it is the operator's
decision, and the automatic creation steps aside.

Two safety properties, because this happens while accounting validates a
document:

* **the posting is never blocked by the warehouse.** The automation runs in a
  savepoint: if the receipt cannot be created or validated (locked stock, a
  misconfigured location…), the bill is posted anyway and the bill chatter
  explains what failed and to match the receipts by hand;
* **nothing is left half-done:** the failed warehouse writes are rolled back,
  so no orphan receipt is left behind.

A receipt generated this way (manually or automatically) is never anonymous:

* its **Origin** is set to the vendor bill it comes from, marked as
  `(bill matching)` — e.g. `BILL/2026/0012 (bill matching)`, or the bill's
  display name when the bill is still a nameless draft;
* the receipt's **chatter** gets a message naming the bill with a clickable
  link back to it, how many bill lines were added, and — for a generated
  receipt — whether it was validated immediately or is waiting to be received.
  When the module generated the receipt on its own (no receipt and no open
  purchase order existed), the message says so.

Feeding an **existing** receipt the same way (step 4 above with an "Existing
Picking" selected) is traced too: the receipt's origin is left untouched, but
the chatter records the bill lines that were added to it and from which bill.

The bill is traced as well: when its posting generated the receipt, the bill
chatter says so with a link to that receipt — so an accountant auditing the
bill sees where the stock came from without leaving the document.

## 3. Undo / Unmatching
If you made a mistake:
1. Go to the Vendor Bill and click the **Matched Items** smart button.
2. Select the mistakenly matched lines.
3. Click **Unmatch Selected**. The Many-to-Many links will be severed, and the quantities will return to the **Match Pickings** view.

## 4. Integration with `stock_picking_invoicing`
If the `stock_picking_invoicing` module is installed, matching or unmatching bill lines automatically synchronizes the invoice state on the related stock moves and pickings. Matched lines are marked as `invoiced`, while partially matched or unmatched lines revert to `2binvoiced`, keeping the picking's billing status consistent without manual intervention.

## 5. Automatic Matching of Referenced Lines
When both sides of a line carry a reference — in Brazil, the NFe (the
electronic invoice the tax authority validates) carries `xPed`, the buyer's
purchase order number, and `nItemPed`, the line number within that order; the
fiscal document import wizard turns that pair into a canonical reference — the
pairing is not a decision anymore: it is arithmetic. The same holds for any
imported document whose line reference identifies a purchase order line. Two
company settings (see *Configuration*) let the system take that decision on its
own:

* **Auto-Match Referenced Lines**: the **Match Pickings** button first matches
  every bill line whose reference is shared by a receipt line, then opens the
  matching screen with what is left;
* **Auto-Match when Posting the Bill**: the same happens automatically when the
  bill is posted, so an imported bill is reconciled without any click.

Only the deterministic cases are matched: a line without a reference, or whose
reference no receipt carries, is left for the operator. A wrong automatic link
would be worse than a click, because it reconciles the bill against the wrong
receipt — and matching a *pending* receipt validates it, like a manual match
does. Every automatic matching writes a note in the bill chatter naming the
receipts and the references used, and can be reverted with **Matched Items ->
Unmatch Selected**.

## 6. Smart Button Counters
The bill form tells where you stand without opening anything:

| Button | Counter |
| --- | --- |
| **Match Pickings** | number of bill lines still to be matched (a partially matched line counts as one) |
| **Matched Items** | number of linked receipt lines; the button is hidden while nothing is matched |

Only the real product lines are counted: the sections, notes, tax and
payment-term lines, the lines without a product and the service lines (which
never go through stock) neither appear in the matching screen nor in the
counters, and they never keep a bill unmatched. A bill made only of services
and notes is simply considered matched.

**Force Matched** / **Reset Force** are actions, so they carry no counter.

**Reading the quantities.** The *Unmatched Qty* of a **bill line** is the
billed quantity still to be covered, and it never goes below zero: a fully
matched line reads `0`, even when the receipt line covering it is larger (one
receipt line can cover several bill lines, and several bill lines can feed
from one receipt line — the link records the pairing, not a quantity per
link). On the **receipt** side the value keeps its sign: a negative *Unmatched
Qty* means the vendor billed more than what was received, which is precisely
the anomaly to look at.

When the matching button finds nothing left to match (because the automatic
matching, or the perfect-quantity shortcut, already matched everything), the
button says so with a notification and reloads the bill instead of opening an
empty matching screen. When something *is* left, the matching screen opens on
exactly those remaining lines.

## 7. How the Matching Screen is Ordered

Inside a product group, the lines are ordered by their **pairing reference**
(the *Match Ref.* column) so that a vendor bill line is immediately followed
by the receipt line(s) carrying the same reference:

```
EUR-D10B-BK-2L          (product group)
  Vendor Bill line      Match Ref. P00235-1     <- bill line
  Forno/IN/00008        Match Ref. P00235-1     <- its receipt, right below
  Vendor Bill line      Match Ref. P00235-3
  Forno/IN/00008        Match Ref. P00235-3
  Forno/IN/00001        Match Ref. -(no ref)    <- not paired: at the bottom
  WH/IN/00493           Match Ref. -(no ref)
```

* the vendor bill lines still come first (of the whole screen, and of their
  pairing group);
* the lines that could not be paired — a bill line without reference, or a
  receipt whose reference no bill line carries — are grouped at the **end** of
  the product group, bills before receipts;
* several bill lines and/or several receipts sharing one reference stay
  together (a supplier splitting one order line over two invoice lines, or one
  order line received in two shipments), the bills first — the reference
  identifies the order line, so a split delivery shows the same reference on
  each shipment, and the *Is Done* column tells them apart;
* matched lines are listed after the unmatched ones (the *Unmatched* filter is
  on by default when opening the screen from a bill).

The reference used for that ordering is the very one displayed in the
*Match Ref.* column: a localization computes it in SQL
(`_get_bill_matching_reference_sql`), otherwise the stored
`matching_reference` field is used.
