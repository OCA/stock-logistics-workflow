When a rule applies to a transfer, its exceptions are shown in three places,
all with the **Exception Name** and **Description** of the rule:

- **On confirmation or validation**, a popup *Outstanding exceptions to
  manage* lists them. Tick *Ignore Exceptions* and confirm to go on, or close
  it and fix the cause first. After ignoring, click *Validate* again to
  validate the transfer. Blocking exceptions cannot be ignored.
- **On the transfer form**, a red banner lists them as *name: description*,
  with *(Blocking exception)* after the blocking ones, and a button *Ignore
  Exceptions* for exception rule managers.
- **In the list of transfers**, the column *Main Exception* shows the first
  exception (lowest sequence); the filter *Blocked in Draft* finds the
  transfers that have one.

Editing the stock moves of a confirmed transfer resets *Ignore Exceptions*,
so the rules are checked again.

To try it with the demo data, open the delivery to *Customer on Credit
Hold*:

1. Click *Mark as To Do*: the rule *Customer on credit hold* applies. It only
   warns: tick *Ignore Exceptions* in the popup to go on.
2. Duplicate the delivery, set the quantity above 10 and click *Mark as To
   Do*: the rule *More than 10 units for a customer on credit hold* applies
   as well. It is blocking, so the exceptions cannot be ignored until the
   quantity is lowered.
