Split moves into different pickings at assignment time if the total weight
of the picking is greater than the maximum weight allowed on the picking type.

Prior to this release only new moves created after the creation of an open picking
were put into a new picking upon assignment if the total weight of the picking
would exceed the maximum weight allowed on the picking type. This release improves
this behavior by also splitting existing moves into different pickings after the
moves have been assigned to a picking. IOW, in a post-assignment step, the system
will split picking lines into different pickings when the total weight is exceeded.
