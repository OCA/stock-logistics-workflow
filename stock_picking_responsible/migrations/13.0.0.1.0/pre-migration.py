# Copyright 2022 Coop IT Easy SC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    cr.execute(
        """
        ALTER TABLE stock_picking ADD IF NOT EXISTS legacy_13_0_responsible_id int;
        UPDATE stock_picking SET legacy_13_0_responsible_id = responsible_id;
    """
    )
