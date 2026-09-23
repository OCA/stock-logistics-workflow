# Copyright 2026 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.stock_move_line_qty_picked.hooks import initialize_picked_quantities


def migrate(cr, version):
    initialize_picked_quantities(cr)
