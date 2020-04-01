# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import SavepointCase


class TestPartnerDeliveryWindow(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner_1 = cls.env['res.partner'].create({'name': 'partner 1'})
        cls.partner_2 = cls.env['res.partner'].create({'name': 'partner 2'})
        cls.DeliveryWindow = cls.env["partner.delivery.time.window"]
        cls.monday = cls.env.ref(
            "base_time_window.time_weekday_monday"
        )
        cls.sunday = cls.env.ref(
            "base_time_window.time_weekday_sunday"
        )
        cls.demo_user = cls.env.ref("base.user_demo")

    def test_delivery_window_warning(self):
        pass

    def test_with_timezone(self):
        pass

