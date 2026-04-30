This module adds two computed fields on `stock.picking` that summarize the
state of the most upstream not-done origin pickings:

- `origin_state`: aggregated state across the origin pickings at the deepest
  level still active (`waiting`, `partially_available`, `assigned` or `done`).
- `origin_state_label`: a display string combining the origin operation type
  name and the translated state label
