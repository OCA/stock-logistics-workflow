Operation types have a default source and destination location, but the
locations of a transfer can be changed freely afterwards, so a transfer can end
up moving stock between locations that have nothing to do with its operation
type. This module adds an option on operation types to restrict their transfers
to those locations: the source and the destination of the transfer must be the
default locations of the operation type or one of their sublocations. A vendor
or customer location is not restricted.
