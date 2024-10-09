As stock operations are computed at a certain moment of time, configuration
can change and the computed destination locations for those operations (that
are not done yet) are incoherent from those configurations changes.

So, the aim of this module is to provide a way to recompute the destination locations
without having to unreserve the picking (that unlock products for being reserved for
another picking).
