# Description

This module bridges the gap between Accounting and Warehouse operations in
Odoo by allowing users to match Vendor Bills against Incoming Stock Pickings
and their Stock Moves, whether or not a Purchase Order exists.

It brings a paradigm native to Odoo 18.0 (Bill Matching) into Odoo 16 but
elevates it by matching against `stock.move` lines instead of
`purchase.order.line`.

## Expected use cases

The module is built around four concrete situations. Recognizing yours tells
you which settings to enable (see *Configuration*) and which part of the
*Usage* documentation to read.

**1. The bill arrives after the goods** (the most common case, and the usual
one with an imported electronic invoice — in Brazil that is the *NFe*, the
electronic invoice the tax authority validates, whose XML carries the invoice
lines in a standardized form; elsewhere it is a supplier portal document, an
EDI, a PDF extraction…). The receipt is already validated: the matching
*links* the bill lines to the receipt lines. Nothing is moved, nothing is
restocked. The operator opens the bill, clicks *Match Pickings*, pairs the
lines (or lets the references do it), and the bill leaves the "to match" list.
Use it even when a purchase order exists — the receipt, not the order, is what
is reconciled.

**2. The bill arrives while the goods are still on their way.** The receipt is
draft/confirmed/assigned: matching additionally *drives the reception* — the
matched quantity is set as done and the receipt is validated, a backorder being
created for whatever the receipt had in excess. This is the "Smart
Auto-Reception" behaviour, and it is the reason the matching works on stock
moves and not only on a link. Optionally, the receipt is validated
automatically (`Auto-Validate Generated Pickings`).

**3. There is no purchase order and no receipt at all** — a small shop, or an
imported invoice for goods that were never encoded in the system. Two ways:
- *Manual:* the *Match Pickings* button opens the matching screen, where
  *Create / Add to Picking* turns the unmatched bill lines into a receipt (and
  validates it if the setting is on);
- *Automatic:* with `Auto-Create the Receipt when Posting the Bill`, posting the
  bill generates that receipt by itself, so an imported document results in
  stock and a reconciled bill with no operator click at all. Nothing is created
  when a purchase order or a receipt candidate exists — matching an existing
  document is a decision, not a formality.

**4. The document carries a line reference.** Electronic invoices commonly
identify the buyer's order line they correspond to — in Brazil the NFe carries
`xPed` (the purchase order number) and `nItemPed` (the line number within that
order); an EDI or a supplier portal has its own variant; and an import wizard
may synthesize one by matching the invoice line to a purchase order line or a
receipt. With `Auto-Match Referenced Lines`, the bill lines whose reference a
receipt line shares are matched automatically — from the *Match Pickings*
button, and/or at posting. Only unambiguous cases are consumed; every automatic
action is traced in the bill chatter.

A single bill may mix all four: some lines already received, some pending, some
without any counterpart. Each line is handled by whichever applies.

## What it actually does

Worth being explicit about the two directions it covers, because they do not
behave the same way:

* **The goods are already received** (the receipt is validated): the matching
  *links* the bill lines to the receipt lines. Nothing is moved, nothing is
  validated again — this is plain reconciliation, and it is the most common
  case when the vendor bill (or its imported electronic version) arrives days
  after the goods.
* **The goods are still pending** (the receipt is draft/confirmed/assigned):
  matching additionally *drives the reception*: the matched quantity is set as
  done on the receipt lines and they are validated, a backorder being created
  for whatever the receipt had in excess. This is the "Smart Auto-Reception"
  behaviour, and it is also why matching is a stock move and not just a link.

## Key Features

* **Unified Matching Interface:** A single screen (SQL View) showing unmatched
  Vendor Bill lines and Receipt lines side-by-side, grouped by product.
* **Ready-to-play demo data:** installing the module with demo data builds a
  small scenario (a received shipment, a pending one of the same order line,
  the bill matching them, and a bill with nothing to match against) so the
  features can be tried without preparing anything — see the usage
  documentation for the three scenarios to play.
* **Many-to-Many Linking:** Leverages the `stock_picking_invoice_link` OCA
  module to allow complex many-to-many relationships (partial billing,
  consolidated billing, one order line received over several receipts).
* **Smart Auto-Reception:** Matching bill lines with pending receipts
  automatically validates the receipt and handles backorders safely using
  native Odoo logic.
* **Already received goods:** matching a validated receipt only links it,
  which is the everyday case (and was the module's blind spot before: a bill
  could not be matched against a receipt that was already validated).
* **Automatic matching of referenced lines:** bills lines carrying a reference
  that a receipt line shares — the line reference of the imported document (in
  Brazil, the NFe `xPed`/`nItemPed`), or the canonical reference the fiscal
  document import wizard synthesized — can be matched automatically, either on
  the *Match Pickings* button or when the bill is posted — see the *Automatic
  Matching* section of the usage documentation. Only unambiguous cases are
  matched, and every automatic action is traced in the bill chatter.
* **Smart button counters:** the bill form shows how many lines still have to
  be matched and how many receipt lines are already linked.
* **Small Shop Replenishment:** Easily generate brand-new Incoming Receipts
  straight from a Vendor Bill — with a single click on the matching screen, or
  automatically when the bill is posted. The generated receipt carries the bill
  as origin and a chatter message linking back to it; a warehouse failure never
  blocks the accounting validation of the bill.
* **Compatibility:** If the `stock_picking_invoicing` module is installed,
  matching or unmatching lines automatically updates the invoice state
  (`invoiced` / `2binvoiced`) on stock moves and pickings.

## Integration / extension points (for other modules)

The matching behaviour can be extended by a localization or a document
importer, with no hard dependency in either direction (everything below is
duck-typed: the feature simply stays inactive when the module is absent).

### `matching_reference`

A `Char` field on both `stock.move` and `account.move.line`, exposed as
**Match Ref.** in the matching screen. It is the key the pairing uses on top of
the product:

* the same non-empty value on both sides means "these two lines belong to the
  same commercial line" (typically a purchase order line, e.g. `P00129-2` for
  the 2nd line of purchase order `P00129` — in Brazil the NFe `xPed`
  (purchase order) and `nItemPed` (line number) fields are exactly that, and a
  localization canonicalizes them into such a key);
* it identifies the **order line, not the shipment**: a line received in
  several deliveries legitimately carries the same reference on each of them,
  and the matching consumes them in order (already received shipments first,
  before validating a pending one). Do NOT try to make the reference unique
  per receipt — the bill side could not follow (an invoice does not say which
  shipment it corresponds to), and reconciling one invoice against several
  deliveries would become impossible;
* an **empty** reference means *unspecified* and acts as a **wildcard**: such a
  line pairs with any line of the same product. This keeps product-only
  matching working when only one side carries a reference;
* exact references are consumed first, wildcards only afterwards.

Both sides must therefore produce the *same canonical string*. A localization
that fills only one side still matches (wildcard), but the precise pairing
requires both.

### Filling the reference: `_get_bill_matching_reference_sql(alias)`

The matching screen is a SQL view, so the reference must be computed by the
database. A module that knows where the reference comes from implements, on
`stock.move` and/or `account.move.line`:

```python
@api.model
def _get_bill_matching_reference_sql(self, alias):
    """Return a SQL expression (varchar) for the given table alias."""
```

`alias` is the SQL alias of the table in the view query (`sm` for
`stock.move`, `aml` for `account.move.line`). The derivation takes precedence;
when it yields nothing (empty or NULL), the stored `matching_reference` field
of the line is used as the fallback — so an importer writing that field
directly still gets pairing, with or without a localization.

Practical notes:

* normalize both sides identically (padding, case, zero-padding…): `P00015-1`
  and `P00015-001` must end up as the same string or they will not pair;
* the reference should identify a *line*, not a document, whenever the document
  can be received and invoiced line by line (a PO name alone is not enough);
* keep the columns it reads indexed if the view is large.

### Overriding the pairing policy: `_get_matching_pairs(aml_lines, sm_lines)`

`picking.bill.line.match._get_matching_pairs` is the pairing core:
it receives the selected bill lines and receipt lines and returns a list of
`(bill line, recordset of receipt lines it may consume)` pairs. Override it to
change the policy itself (e.g. match on an attribute other than the product, or
implement a completely different algorithm); the caller
(`action_match_lines`) then distributes the quantities, links the lines,
validates the pending receipts and computes the backorders.

### Quantities, precision

`MATCHING_PRECISION` (ORM side) and `MATCHING_EPSILON_SQL` (SQL view side) are
the two thresholds used to decide that a quantity has been consumed; they are
intentionally small (0.001) because quantities are matched, not rounded: a
one-unit shortage must NOT be reported as matched.
