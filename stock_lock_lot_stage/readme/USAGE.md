Only users in the *Block/unblock Lots* security group can change lot stages.
The blocked flag is read only on the form, as it is now managed through the
stages.

Stage changes are tracked in the messages area, providing an audit log.

New lots start in the Approved or Pending stages, depending on the default
Blocked flag, as set on the Product or Category configuration. Refer to the
Stock Lock Lot documentation for details.

A *Partial Approved Quantity* field is available to set the approved quantity,
when less than the total lot quantity. This is only editable by the
Block/unblock Lot security group.

When a partial approved quantity is set, the lot
can only be moved to locations that don't allow locked lots up to the approved
amount. Excess quantities must be moved to nonconformity zones.
