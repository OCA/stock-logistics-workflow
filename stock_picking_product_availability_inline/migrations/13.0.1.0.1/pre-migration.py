# Copyright 2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade  # pylint: disable=W7936

from odoo.addons.stock_picking_product_availability_inline.hooks import pre_init_hook


@openupgrade.migrate()
def migrate(env, version):
    # Pre-create column for avoiding to trigger the compute
    pre_init_hook(env.cr)
