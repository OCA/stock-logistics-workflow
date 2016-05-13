# -*- coding: utf-8 -*-
# © 2016 Lorenzo Battistini - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def migrate(cr, version):
    if not version:
        return
    openupgrade.rename_columns(
        cr, {
            'stock_picking_package_preparation_line': [
                ('product_uom', 'product_uom_id'),
            ],
        }
    )
