- Only the source and destination locations of the transfer are checked. The
  standard views limit the locations of its operations to sublocations of
  those, but they are not checked when they are set by other means.
- Only the returns created from a transfer, and their backorders, can go back
  the way the original transfer came. Other reverse transfers need the
  operation type to have a **Returns Type** that allows them: the one created
  when the demand of a partially processed move is reduced, the refunds of a
  point of sale, or a copy of a return (a duplicate, or the transfer created
  when part of a return is split or added to a wave).
- The transfers that resupply a subcontractor go to the subcontracting location
  of that partner. An operation type used for them should not be restricted
  when subcontractors have their own location outside its destination location.
- Odoo sets the default locations of the operation types of a warehouse again
  when the warehouse is reconfigured, for example when its steps or its short
  name change, or when some modules are installed. That reconfiguration is
  rejected while transfers in progress or rules of its restricted operation
  types do not fit the resulting locations, also when the locations of an
  operation type had been customized and Odoo sets the standard ones back.
- Moving a location under another parent location, or changing its type, does
  not check the transfers and rules that use it.
