# Copyright 2024 Moduon Team S.L. <info@moduon.team>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/LGPL).
from odoo import SUPERUSER_ID, api, tools


def migrate(cr, version):
    # Update the `expiration_date` field definition in the `stock_move_line` table
    env = api.Environment(cr, SUPERUSER_ID, {})
    sml_model = env["stock.move.line"]
    sml_columns = tools.table_columns(env.cr, sml_model._table)
    sml_model._fields["expiration_date"].update_db(sml_model, sml_columns)
    # Don't need to recompute (flush) fields onto the DB because:
    # If the field is required, will have been recomputed.
    # If the field is not required, doesn't need to be flushed in the DB.
