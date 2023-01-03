# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.stock_picking_progress.hooks import setup_move_progress


def migrate(cr, version):
    if not version:
        return
    setup_move_progress(cr)
