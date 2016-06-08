# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def migrate(cr, version):
    if not version:
        return
    openupgrade.rename_columns(
        cr, {
            'stock_move': [
                ('invoice_line_id', None),
            ],
            'stock_picking': [
                ('invoice_id', None),
            ],
        }
    )
