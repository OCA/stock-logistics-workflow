- When migrating from `stock_move_actual_date`, the legacy `actual_date` is a
  local date, but the timezone it was entered in is not recorded. The migration
  assumes the timezone of the record's company (UTC if the company has none) to
  convert it to the UTC effective date. Records entered by users in a different
  timezone than their company may end up a day off and should be checked after
  the migration.
- Editing the effective date of a done record does not change the date of
  journal entries already posted, unlike `stock_move_actual_date`.
