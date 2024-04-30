# Copyright 2023 ForgeFlow, S.L.
# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

from odoo.addons.stock_picking_invoice_link.init_hook import (
    _create_picking_count,
    _populate_picking_count,
)


@openupgrade.migrate()
def migrate(env, version):
    """Pre-create the delivered_count field for performance"""
    _create_picking_count(env.cr)
    _populate_picking_count(env.cr)
