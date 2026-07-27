## 18.0.1.0.2 (2026-07-27)

- Fix the cost price of oversold products. When the accumulated quantity is
  zero or negative there are no units left to average against, so the cost of
  the incoming move becomes the new average, which is also the cost core's
  negative stock vacuum uses to settle the deficit once enough real stock
  arrives. Odoo weighted it against the negative quantity instead, and dividing
  by that negative denominator let a receipt lower the average, or even turn it
  negative and, from there, make every outgoing move add value to the stock
  valuation.
- Let core's negative stock vacuum run again for average cost products. It used
  to be disabled for every cost method, so nothing corrected the deficit once
  real stock arrived.
