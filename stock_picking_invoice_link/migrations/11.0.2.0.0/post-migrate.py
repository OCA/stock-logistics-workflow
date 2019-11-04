# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.m2o_to_x2m(env.cr, env['stock.move'], 'stock_move',
                           'invoice_line_ids', 'invoice_line_id')
