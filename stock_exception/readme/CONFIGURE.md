To create the rules, go to *Inventory > Configuration > Stock Exception
Rules* (needs the group *Exception manager*). A few example rules are
provided archived; activate them or create new ones.

For each rule, set:

- **Exception Name** and **Description**: the text shown to the user. The
  name is the short title, the description says what to do about it. Both
  are translatable.
- **Apply on**: *Stock Picking* to check the transfer, *Stock Move* to check
  each of its lines.
- **Exception Type**: *By domain* (a filter, e.g.
  `[('partner_id', '=', False)]`), *By python code* (set `failed = True`
  when the exception applies; the record is `self`) or *By method* (a
  method provided by another module).
- **Sequence**: the order of the rules; the first exception found is the one
  shown in the transfer list.
- **Is Blocking**: when ticked, the exception cannot be ignored.
