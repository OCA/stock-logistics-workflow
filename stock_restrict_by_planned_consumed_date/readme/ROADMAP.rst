* Today we restrict the reservation based on the lot expiration date, but in
  some circumstances we probably want something configurable to base the restriction on `use_date` (best before). 
* Find a nice way to be compliant with both modules `product_expiry`
  and `product_expiry_simple`. This would require to launch unittest twice with both
  modules.
