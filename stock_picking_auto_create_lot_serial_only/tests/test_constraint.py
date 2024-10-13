# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase

from odoo.addons.stock_picking_auto_create_lot.tests.common import (
    CommonStockPickingAutoCreateLot,
)


class TestProductAutoLotConstraint(CommonStockPickingAutoCreateLot, TransactionCase):
    def test_constraint_product(self):
        # Product constraint
        with self.assertRaises(ValidationError):
            self._create_product()
