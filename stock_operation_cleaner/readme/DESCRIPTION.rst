This module remove pack operations on stock move cancellation. This avoid
to keep useless pack operations into the database. In odoo > 10, these
operations (renamed as stock.move.line) are removed on stock move cancellation.
