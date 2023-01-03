# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import SUPERUSER_ID, api

from odoo.addons.stock_picking_progress.hooks import setup_move_progress_post


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    setup_move_progress_post(env)
