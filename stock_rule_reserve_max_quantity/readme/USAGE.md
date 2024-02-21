To use this module, you need to:

1. Enter on debug mode
2. On your Warehouse, activate 2 or 3 steps for Outgoing Shipments
3. Go to Warehouse routes and open *pick + ship* (2 steps) or *pick + pack + ship* (3 steps)
4. Activate Reserve Max Quantity under the Propagation group in all rule steps except the first one
5. Create a sale with a storeable product and confirm it and has enough stock.
6. Go to the first picking and set quantity done over the quantity demanded and validate it.
7. Check that the next picking will reserve the entire quantity previously made instead of the quantity demanded.
