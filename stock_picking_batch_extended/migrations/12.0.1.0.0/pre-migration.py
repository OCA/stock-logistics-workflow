# Copyright 2019 Tecnativa - Pedro M. Baeza
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from openupgradelib import openupgrade


_field_renames = [
    ('stock.warehouse', 'stock_warehouse', 'default_picker_id',
     'default_user_id'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
