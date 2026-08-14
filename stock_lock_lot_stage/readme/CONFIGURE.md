On *Inventory > Configuration > Lot Stages*, the lot stages can be configured.
By default the stages proposed are: Pending, Testing, Partially Approved,
Approved, Rejected.

These stages map to a Blocked status, automatically updating the corresponding
flag in the lot. Only the Approved stage unblocks a lot.

When installing this module, all lots will be initialized with the "Approved"
or "Pending" stage, depending on the value of the Blocked flag.
When installing the first time, existing lots are not locked by default,
so existing lots are expected to start as Approved.
