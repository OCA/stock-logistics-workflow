# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import http
from odoo.http import request


class StockWeighing(http.Controller):
    @http.route("/stock_weighing/start_screen", auth="user", type="json")
    def stock_weighing_start_screen(self):
        """Returns the banner for the weighing options"""
        return {
            "html": request.env.ref(
                "stock_weighing.stock_weighing_start_screen"
            )._render(
                {
                    "actions": request.env[
                        "weigh.operation.selection"
                    ]._get_weighing_start_screen_actions()
                }
            )
        }
