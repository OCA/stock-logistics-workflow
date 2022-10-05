# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase

from .common import PutawayHookCommon


class TestPutawayHook(PutawayHookCommon, TransactionCase):
    def test_putaway_hook(self):
        """
        The first location has no strategy nor alternative one
        The _get_putaway_strategy() should return that location
        """
        strategy = self.location_internal_1._get_putaway_strategy(self.product)
        self.assertEqual(
            self.location_internal_1,
            strategy,
        )

    def test_putaway_hook_context(self):
        """
        The second location has no strategy nor alternative one
        But _putaway_<field> is passed in context.
        Should return the second location
        """
        strategy = self.location_internal_1.with_context(
            _putaway_foo=True
        )._get_putaway_strategy(self.product)
        self.assertEqual(
            self.location_internal_1,
            strategy,
        )

    def test_putaway_hook_alternative(self):
        """
        The third location has no strategy but a foo alternative one
        Should return the location from the putaway
        """
        strategy = self.location_internal_3.with_context(
            _putaway_foo=True
        )._get_putaway_strategy(self.product)
        self.assertEqual(
            self.location_internal_shelf_3,
            strategy,
        )
