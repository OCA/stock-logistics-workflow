# -*- coding: utf-8 -*-
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, SUPERUSER_ID
from openupgradelib import openupgrade


def migrate(cr, version):
    if not version:
        return
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        openupgrade.m2o_to_x2m(
            cr, env['stock.move'], 'stock_move', 'invoice_line_ids',
            openupgrade.get_legacy_name('invoice_line_id'))
        openupgrade.m2o_to_x2m(
            cr, env['stock.picking'], 'stock_picking', 'invoice_ids',
            openupgrade.get_legacy_name('invoice_id'))
