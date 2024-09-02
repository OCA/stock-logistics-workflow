When a product is tracked by lot or serial number and is returned by a customer,
it’s crucial to clearly indicate to the user which lot or serial number can be
accepted. This way, we prevent user from receiving a product with a lot or
serial number different from the original delivery.

This module enhances the return process by creating a separate return line for
each product/lot and automatically pre-filling it with the lot from the original delivery.
It relies on the `Stock Restrict Lot <https://github.com/OCA/stock-logistics-workflow/tree/16.0/stock_restrict_lot>`__
module to enforce accurate tracking, ensuring that the reception order reflects
the correct lot or serial number that should be received.
