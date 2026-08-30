Handle boxes/kits of components, that can be moved as a package,
but have the stock managed at the individual components.
This allows, for example, to track the serial numbers for the individual components.

Example:

- "Widget" is received in a box, containing Parts A, B and C.
  Parts A and B are serial number controlled, but part C is not.
  The serial numbers are barcoded and in the box labels.
- When receiving, we want to select the Kit product,
  type the quantity to receive, and then scan the barcodes for each box.
