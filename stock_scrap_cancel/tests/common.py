# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class Basecommon(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
