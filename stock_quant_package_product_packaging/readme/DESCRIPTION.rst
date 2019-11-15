This module allows to define on a Product Package (`stock.quant.package`), a
Packaging Type (`product.packaging`) that is linked to a product, if said
package only contains Quants (`stock.quants`) from this product, and the sum of
the quants quantities is equal to the Packaging quantity.

If such a packaging exists, it will be automatically assigned to a package after
the move is set to done.
