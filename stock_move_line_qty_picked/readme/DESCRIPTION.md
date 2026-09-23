This module adds a  `qty_picked` field on `stock.move.line` to allow scanning
different quantities without having to update the `quantity` field, what would
modify existing reservations.

It is meant to restore the behaviour we had in previous versions with `qty_done`
field, but using another name to avoid clashing with the field defined in Odoo
Enterprise's Stock barcode module.
