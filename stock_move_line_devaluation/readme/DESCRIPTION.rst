This module provides a stock withdrawal valuation report that calculates
the monetary value of outgoing stock moves based on pricelist pricing.

Before displaying the report, a wizard allows the user to:

* Select a customer (optional) — the customer's default pricelist is loaded
  automatically.
* Choose or override the pricelist for price calculations.
* Define a date range to filter stock withdrawals.

The report:

* Shows only outgoing (customer delivery) stock move lines that are in
  "done" state.
* Automatically excludes fully returned deliveries and adjusts quantities
  for partial returns, showing only the net quantity.
* Calculates the unit price from the selected pricelist (e.g. cost × 1.8
  if configured) and the total value per line.
* Displays totals so the user can see how much a customer owes based on
  stock withdrawals.
* Supports tree and pivot views with grouping by customer, product, date,
  and transfer.
