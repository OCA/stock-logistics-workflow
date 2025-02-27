By default Odoo takes the Shipping Policy set in the procurement group,
or fallbacks on the one configured on the Operation Type.

This module adds a Force Shipping Policy field on Operations Types to ensure
transfers will take the policy according to their types, ignoring the one set
on the Procurement Group.

This is especially useful if you use a multi-steps setup (like pick-pack-ship)
and you want the pick and/or pack operation to wait for all goods to be
available no matter what was the sales shipping policy.
