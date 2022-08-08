# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests.common import SavepointCase


class ResConfigSettingsCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.company = cls.env.company

        cls.settings = cls.env["res.config.settings"].create(
            {"is_moves_assignation_limited": True, "moves_assignation_horizon": 2}
        )
