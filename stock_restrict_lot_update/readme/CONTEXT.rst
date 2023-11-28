In a setup where lot selection is managed both at sale level and warehouse level
(but the final call is made by warehouse flows), there can be the need to select
a different lot than the one set in sale order line. As current sale order lot
selection modules are depending on stock_restrict_lot (which doesn't allow to
select a different lot in picking), this module allows to limit the restriction
to for specific products.
