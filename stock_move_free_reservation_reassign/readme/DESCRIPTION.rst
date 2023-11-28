In the logistics workflow, some operations could make quants no more available
for the picking. This is the case for example when the quantities into a location
are updated by an inventory adjustment. In such a case, Odoo will unreserve the
move lines linked to the quants that are no more available. This module extends
this behavior by trying to automatically reserve the move lines after the
freeing of the existing reservation.
