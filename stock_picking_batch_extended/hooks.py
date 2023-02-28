# Copyright 2019 Camptocamp - Iryna Vyshnevska
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    company = env["res.company"].search([])
    company.write({"use_oca_batch_validation": True})
