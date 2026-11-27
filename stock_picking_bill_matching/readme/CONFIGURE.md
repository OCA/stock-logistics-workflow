# Configuration

Settings are per company, under **Inventory -> Configuration -> Settings ->
Bill Matching** (they also apply to the bills of that company only).

| Setting | Default | What it does |
| --- | --- | --- |
| **Auto-Create Picking on Match** | off | If a bill has no open receipt to match against (and no open purchase order for that vendor), clicking **Match Pickings** creates the missing receipt from the bill lines instead of opening the matching screen. |
| **Auto-Validate Generated Pickings** | off | The receipts that matching has to validate (a pending receipt being reconciled with a bill) are validated straight away instead of being left to be validated by hand. |
| **Auto-Match Referenced Lines** | off | The bill lines carrying a matching reference are matched automatically against the receipt lines carrying the **same** reference. See the *Automatic Matching* usage section. |
| **Auto-Match when Posting the Bill** | off | Also run the automatic matching when a vendor bill is posted, so an imported bill (a Brazilian NFe, or any document whose import wizard synthesizes the reference) is reconciled without any click. Requires the setting above. |
| **Auto-Create the Receipt when Posting the Bill** | off | Small shop flow: when a posted bill has lines with nothing to match against (no purchase order, no receipt at all for the vendor), the receipt is created from those lines. Combined with **Auto-Validate Generated Pickings**, the bill results in stock and a reconciled document with no manual step. Nothing is created when a purchase order or a receipt candidate exists. |

## Recommended presets

**Warehouse-driven** (a purchase order and receipts exist; an operator
reconciles): keep everything off, except **Auto-Validate Generated Pickings**
if the reception must be validated by the matching.

**Imported documents with references** (the Brazilian NFe, whose `xPed`/
`nItemPed` fields name the purchase order and its line, or any document whose
import wizard synthesizes references): **Auto-Match Referenced Lines** +
**Auto-Match when Posting the Bill**. The operator only handles the lines the
references could not resolve.

**Small shop, imported documents, nothing encoded in Odoo**: the two settings
above **plus Auto-Create the Receipt when Posting the Bill** and
**Auto-Validate Generated Pickings**. Posting an imported bill then creates and
validates the missing receipt, and links it to the bill.

## What the automatic matching will and will not do

It only consumes the deterministic cases:

* the bill line has a **non-empty** reference, **and**
* at least one receipt line of the same product, for the same vendor, carries
  **exactly that reference**.

Everything else stays for the operator: lines without a reference (the matching
would then fall back to a product-only guess), lines whose reference no receipt
carries, and quantities that do not add up — a wrong automatic match would
reconcile the bill against the wrong receipt, which is worse than a click.

Being a matching operation, it has the same effect as a manual match: a pending
receipt is validated (and a backorder created for its excess quantity), an
already validated receipt is only linked. Every automatic matching is traced in
the bill chatter, and it can always be undone with **Matched Items → Unmatch
Selected**.

## The posting never fails because of the warehouse

The warehouse automation triggered at posting (the automatic matching and the
automatic receipt creation) runs inside a savepoint and under
`try/except UserError, ValidationError`:

* a warehouse problem (locked stock, a receipt that cannot be validated, a
  misconfigured location…) posts the bill anyway — accounting must not be
  blocked by the warehouse — and writes in the bill chatter what failed and
  what to do (match the receipts by hand);
* whatever the automation had half-written is rolled back: no orphan receipt
  is left behind.
