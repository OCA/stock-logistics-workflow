Allow to archive/unarchive a lot.

A lot cannot be archived while an internal or transit location holds quantity
of it, much as Odoo refuses to archive a location that holds stock. Stock that has left the
company (sold, scrapped, returned to the supplier) does not count. Scripts that
must archive regardless can pass `do_not_check_quant` in the context, the key
Odoo uses for the location check.
