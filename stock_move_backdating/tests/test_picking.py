# Copyright 2015-2016 Agile Business Group (<http://www.agilebg.com>)
# Copyright 2018 Alex Comba - Agile Business Group
# Copyright 2023 Simone Rubino - TAKOBI
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged

from .common import TestCommon


@tagged("post_install", "-at_install")
class TestPicking(TestCommon):
    def test_date_backdating_yesterday(self):
        date_backdating = self._get_datetime_backdating(1)
        self._transfer_picking_with_dates(date_backdating)

    def test_date_backdating_last_month(self):
        date_backdating = self._get_datetime_backdating(31)
        self._transfer_picking_with_dates(date_backdating)

    def test_date_backdating_future_wizard(self):
        date_backdating = self._get_datetime_backdating(-1)
        with self.assertRaises(ValidationError):
            self._transfer_picking_with_dates(date_backdating)

    def test_date_backdating_future(self):
        date_backdating_1 = self._get_datetime_backdating(-1)
        date_backdating_2 = self._get_datetime_backdating(-2)
        with self.assertRaises(UserError):
            self._transfer_picking_with_dates(date_backdating_1, date_backdating_2)

    def test_different_dates_backdating(self):
        date_backdating_1 = self._get_datetime_backdating(1)
        date_backdating_2 = self._get_datetime_backdating(2)
        self._transfer_picking_with_dates(date_backdating_1, date_backdating_2)
