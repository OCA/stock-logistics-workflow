This module is similar to the official `product_expiry <https://github.com/odoo/odoo/tree/14.0/addons/product_expiry>`_ module that adds support for *Expiry Dates* on products, but it is both simpler and better:

* Only one *Expiry Date* field instead of 4 fields (Expiration Date, Best before Date, Removal Date, Alert Date)!
* Use date field instead of datetime field for *Expiry Date*.
* No automatic computing of Expiry Date based on a delay configured on product because it is not used most of the time (for manufacturing companies, the rules that control expiry dates are usually more complex than that ; for reseller companies, they have to copy the expiry date written on the good when they receive it in their warehouse).

This modules keeps the main feature of the official *product_expiry* module: the support of FEFO (First Expiry First Out).

I decided to develop this module because, after implementing *product_expiry* at several companies, I noticed that I spent more time inheriting the official *product_expiry* module to make always the same kind of changes that re-developping a simpler and better alternative.
