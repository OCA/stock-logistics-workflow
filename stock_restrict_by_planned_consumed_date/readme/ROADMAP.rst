* Today we restrict expiration lot date must be greater thant planned consumed date in
  some circumstance we probably want something flexible based on product configuration and
  probably based on use_date (best before). 
* Find a nice way to be compliant with both modules `product_expiry`
  and `product_expiry_simple`. This would require to launch unittest twice with both
  modules.
