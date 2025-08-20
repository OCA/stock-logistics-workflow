# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def pre_init_hook(env):
    # Create related fields for already populated databases with
    # thousands of records as grn is not yet stored on picking level
    if openupgrade.column_exists(env.cr, "stock_move", "grn_id"):
        return
    fields_spec = [("grn_id", "stock.move", False, "many2one", "integer", "stock_grn")]
    openupgrade.add_fields(env, fields_spec)
