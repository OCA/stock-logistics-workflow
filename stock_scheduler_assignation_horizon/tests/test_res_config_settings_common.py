# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests.common import SavepointCase


class ResConfigSettingsCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.settings = cls.env["res.config.settings"].create({})
        # enable global params
        cls.env["ir.config_parameter"].sudo().set_param(
            "stock_scheduler_assignation_horizon.stock_horizon_move_assignation", True
        )
        cls.env["ir.config_parameter"].sudo().set_param(
            "stock_scheduler_assignation_horizon.stock_horizon_move_assignation_limit",
            2,
        )
