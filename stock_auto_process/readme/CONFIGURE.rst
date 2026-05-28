The user must be assigned the **Stock Auto Process** extra right in
*Settings > Users > [user] > Extra Rights* to configure rules.

To configure auto-processing rules, go to *Inventory > Operations >
Auto Process Rules* and create one record per condition you want to
automate. A rule has the following fields:

* **Operation Types**: pickings of the listed operation types are eligible.
  Leave empty to apply to all operation types.
* **Domain**: additional ``stock.picking`` domain to narrow the selection
  further (for example, only pickings without an owner, or only those for
  a specific partner).
* **Company**: the rule applies only to pickings of this company.
* **Auto Confirm**: runs ``action_confirm`` on ``draft`` pickings.
* **Auto Assign**: reserves stock for ``confirmed`` or
  ``partially_available`` pickings.
* **Auto Validate**: validates ``assigned`` or ``partially_available``
  pickings.
* **Create Backorder**: when auto-validating a partially available picking,
  controls whether a backorder is created for the unfulfilled quantity.
  When disabled, the picking is validated as-is and the unfulfilled
  quantity is discarded.
* **Sequence**: rules are evaluated in this order on each cron run.
