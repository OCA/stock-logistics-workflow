# Copyright 2022 Coop IT Easy SC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    cr.execute("""
        UPDATE stock_picking SET responsible_id = temporary_responsible;
        ALTER TABLE stock_picking DROP COLUMN temporary_responsible;
    """)
