When the *Variable Quantity* option is enabled on a picking type, validate that
operation with the actual processed quantity.

If the validated quantity differs from the original demand, the module updates
the chained downstream moves to match that new quantity.

Corrections made on the detailed operations of a validated operation are also
propagated: the demand of the pending chained moves is updated and they are
reserved again. When a chained move was already picked with a quantity
different from its reservation, the picked quantity is kept and a message is
logged on its transfer so it can be reviewed.
