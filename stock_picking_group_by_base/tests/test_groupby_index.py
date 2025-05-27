# Copyright 2022 ACSONE SA/NV
# Copyright 2025 Juan Alberto Raja<juan.raja@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from psycopg2.errors import LockNotAvailable

from odoo.tests.common import TransactionCase


class TestPickingGroupBy(TransactionCase):
    def setUp(self):
        super().setUp()
        self.stock_picking_model = self.env["stock.picking"]

    def test_index(self):
        index_name = "stock_picking_groupby_key_index"
        self.env.cr.execute(
            "SELECT indexname FROM pg_indexes WHERE indexname = %s", (index_name,)
        )
        self.assertTrue(self.env.cr.fetchone())

    @patch("odoo.addons.stock_picking_group_by_base.models.stock_picking._logger")
    def test_create_index_lock_not_available(self, mock_logger):
        """Test LockNotAvailable exception"""
        with patch.object(
            self.env.cr, "execute", side_effect=[None, LockNotAvailable()]
        ):
            self.stock_picking_model._create_index_for_grouping()
            mock_logger.warning.assert_called_once()

    def test_create_index_other_exception(self):
        """Test other exceptions are raised"""
        # Crear nuevo cursor para evitar conflictos con savepoints
        with self.env.registry.cursor() as test_cr:
            test_env = self.env(cr=test_cr)
            test_model = test_env["stock.picking"]
            with patch.object(test_cr, "execute", side_effect=RuntimeError("Error")):
                with self.assertRaises(RuntimeError):
                    test_model._create_index_for_grouping()
