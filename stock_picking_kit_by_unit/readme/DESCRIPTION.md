Handle boxes/kits of components, that can be moved as a package, but
have the stock managed at the individual components. This allows, for
example, to track the serial numbers for the individual components.

Adds a "Kit Ops" button on stock pickings that opens a dedicated
Kit Operations list view. This view shows the move lines for kit
components sorted per kit unit (box) instead of per component,
making it easy to process each box sequentially.

Example:

- "Widget" is received in a box, containing Parts A, B and C. Parts A
  and B are serial number controlled, but part C is not. The serial
  numbers are barcoded and in the box labels.
- When receiving, open Kit Operations to see all components grouped
  per box, enter the serial numbers for each box, and then pack them.
