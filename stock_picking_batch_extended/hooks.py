# Copyright 2019 Camptocamp - Iryna Vyshnevska
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    env["res.company"].search([]).write({"use_oca_batch_validation": True})
