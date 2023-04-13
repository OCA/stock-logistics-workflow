# Copyright 2022 Camtocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID, api
from odoo.tools.sql import column_exists


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    if column_exists(cr, "res_company", "is_moves_assignation_limited"):
        query = "SELECT is_moves_assignation_limited FROM res_company;"
        cr.execute(query)
        res = cr.fetchall()

        create_param = [True for x in res if x[0] is True]
        if create_param:
            param = env["ir.config_parameter"].create(
                {
                    "key": "stock_scheduler_assignation_horizon.stock_horizon_move_assignation",
                    "value": True,
                }
            )
            env["ir.model.data"].create(
                {
                    "name": "is_moves_assignation_limited",
                    "module": "stock_scheduler_assignation_horizon",
                    "res_id": param.id,
                    "model": "ir.config_parameter",
                    "noupdate": True,
                }
            )
            query = "SELECT moves_assignation_horizon FROM res_company;"
            cr.execute(query)
            res = cr.fetchall()
            limit = [x[0] for x in res if x[0] and x[0] > 0]
            if limit:
                param = env["ir.config_parameter"].create(
                    {
                        "key": "stock_scheduler_assignation_horizon."
                        "stock_horizon_move_assignation_limit",
                        "value": limit[0],
                    }
                )
                env["ir.model.data"].create(
                    {
                        "name": "stock_scheduler_assignation_horizon",
                        "module": "stock_scheduler_assignation_horizon",
                        "res_id": param.id,
                        "model": "ir.config_parameter",
                        "noupdate": True,
                    }
                )
