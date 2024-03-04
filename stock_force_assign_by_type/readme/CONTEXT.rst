The background context for this module is that we need to pay for something that leaves
our warehouse (the supplier charges waste management fees), which is something not
supported by Odoo. So we need to:

* Make a purchase order from which we can generate a supplier invoice.
* Only an inbound picking will complete the quantities delivered (received) on the purchase order.
* Reserve the correct lots from our stock automatically as in a delivery picking
  (this is what this module allows us to do).
* To be able to reassign/unreserve as in a normal delivery. For that reason we overwrite the domain.
