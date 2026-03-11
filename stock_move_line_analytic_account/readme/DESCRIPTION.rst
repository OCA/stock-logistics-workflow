This module computes and stores the analytic account on stock move lines,
extracting it from the stock move's analytic distribution. It exposes this
field in the stock move line list and search views.

It allows users to:

* display the analytic account in moves history;
* search stock move lines by analytic account;
* group stock move lines by analytic account.

When a stock move has multiple analytic accounts in its distribution, the
account with the highest percentage is used.
