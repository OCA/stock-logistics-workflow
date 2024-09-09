# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


def migrate(cr, version):
    if not version:
        return
    cr.execute("UPDATE stock_warehouse set mto_as_mts = true;")
