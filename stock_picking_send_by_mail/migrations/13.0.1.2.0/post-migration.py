# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr,
        "stock_picking_send_by_mail",
        "migrations/13.0.1.2.0/noupdate_changes.xml",
    )
    openupgrade.delete_record_translations(
        env.cr, "stock_picking_send_by_mail", ["email_template_stock_picking"],
    )
