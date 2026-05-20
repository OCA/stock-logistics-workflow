This module makes the effective date (*Date Done*) of stock transfers and
scraps editable and auditable.

Odoo 19 already lets you edit the effective date of a done transfer and
propagates it to the related stock moves and move lines. On top of that, this
module adds:

- **Original Effective Date** (`origin_date_done`) on transfers and scraps: the
  real processing timestamp, kept as an audit reference after the effective
  date is edited.
- **A permission group** ("Modify Effective Date on Done Records") required to
  edit the effective date of done records. Dates in a hard-locked fiscal period
  cannot be changed, for transfers and scraps alike.
- **Editable scrap date** (read-only and stamped with the validation time in
  standard Odoo), propagated to the scrap move and its line.
- **Pre-set effective date**: a date entered before validation is kept, and the
  stock journal entry is dated on it.

This module changes the date only, not the inventory valuation. For
foreign-currency purchase receipts, also install
[`purchase_stock_date_done_revaluation`](https://github.com/OCA/purchase-workflow/tree/19.0/purchase_stock_date_done_revaluation)
so that the value follows the edited date's exchange rate.
