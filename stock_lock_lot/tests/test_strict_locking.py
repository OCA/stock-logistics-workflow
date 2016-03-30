# -*- coding: utf-8 -*-
# © 2016 Numérigraphe
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from . import test_locking
from openerp import exceptions


class TestStrictLocking(test_locking.TestLockingUnlocking):
    """Redo all the same tests as stock_lock_lot, and some more"""
    def setUp(self):
        super(TestStrictLocking, self).setUp()
        self.env['stock.config.settings']._write_or_create_param(
            'stock.lock.lot.strict', True)

    def test_force_assign(self):
        """We mustn't move locked lots even by forcing availability"""
        self.lot.button_lock()
        self.picking_out.force_assign()
        with self.assertRaises(exceptions.ValidationError):
            self.picking_out.action_done()

    def test_done_directly(self):
        """We mustn't move locked lots by skipping to done state"""
        self.lot.button_lock()
        with self.assertRaises(exceptions.ValidationError):
            self.picking_out.move_lines[0].action_done()
