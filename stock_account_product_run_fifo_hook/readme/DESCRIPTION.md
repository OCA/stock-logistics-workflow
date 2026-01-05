This module adds hook points in the FIFO valuation process to add more flexibility
in the information that is stored and processed during FIFO candidate calculations.

In Odoo 19, the valuation logic has shifted from `stock.valuation.layer` to `stock.move`.
This module provides extension points for custom modules to:

- Access FIFO candidate move information during valuation
- Enrich stock moves with custom candidate data
- Control standard price update logic during FIFO operations

