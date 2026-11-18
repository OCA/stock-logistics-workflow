Companies in a corporate group may source stock from a sister entity as well as
from external vendors. Stock received from a group company carries that entity's
internal margin, which must be excluded from consolidated valuation to avoid
double-booking costs and sales between entities.

The source vendor is only reachable from the valuation layer through a multi-level
relation, which is impractical for filtering. Storing it directly on each layer
makes it easy to filter out intragroup-sourced valuation, and provides a readily
available dimension for supplier-based valuation analysis in general.
