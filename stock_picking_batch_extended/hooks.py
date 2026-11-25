# Copyright 2019 Camptocamp - Iryna Vyshnevska
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def post_init_hook(env):
    env["res.company"].search([]).write({"use_oca_batch_validation": True})
