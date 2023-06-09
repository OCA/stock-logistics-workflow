This module adds a 'scheduled action' that periodically checks that the
'scheduled date' of the pickings belonging to certain 'operation types'
is prior to the datetime that these checks are performed. For each of the
pickings that meet this condition, an activity will be created indicating
that the 'scheduled date' must be updated.

The operation types that will be taken into account are those that you
determine by checking a specific checkbox for that.
