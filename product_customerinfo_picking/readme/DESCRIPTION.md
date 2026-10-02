Based on product_customerinfo, this module loads in every
stock move the customer code and customer name defined in the product.

The lookup respects the partner hierarchy (delivery addresses resolve to their
parent account) and falls back to the warehouse's linked partner when the
picking partner has no matching code — covering consignment warehouse scenarios
where the transfer counterpart differs from the warehouse owner.
