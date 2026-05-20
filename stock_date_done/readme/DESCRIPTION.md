This module makes the effective date (*Date Done*) of stock transfers and
scraps a first-class, auditable value.

Odoo 19 already lets you edit `date_done` on a *done* transfer and propagates
it natively to the related stock moves and move lines
(`picking.date_done` → `move.date` → `move_line.date`). On top of that, this
module adds:

- **`origin_date_done`** on transfers and scraps: the real processing timestamp
  captured the first time the record is done. It is never overwritten, so it
  stays available as an audit reference even after the effective date is edited.
- **A permission group** ("Modify Effective Date on Done Records") that gates
  editing the effective date of *done* records, composing with the native hard
  fiscal-lock check.
- **Editable scrap date**: scraps gain an editable effective date (native leaves
  the scrap date read-only and stamped to `now()`), which is propagated to the
  scrap move and its line.
- **Honoring a pre-set effective date** at validation: when a value is supplied
  before the record is done, it is kept instead of being overwritten with
  `now()`.

**Foreign-currency purchases — install the revaluation module too.** This
module governs the *date* only; it does **not** change inventory *valuation*
(the same as native Odoo). So when you edit the effective date of a
foreign-currency purchase receipt, the date moves but the value stays at the
rate of the original validation date — date and value no longer agree. To make
the value follow the edited date (re-derived at that date's exchange rate),
also install
[`purchase_stock_date_done_revaluation`](https://github.com/OCA/purchase-workflow/tree/19.0/purchase_stock_date_done_revaluation).
For company-currency operations this does not matter (the rate is always 1), so
this module on its own is sufficient.
