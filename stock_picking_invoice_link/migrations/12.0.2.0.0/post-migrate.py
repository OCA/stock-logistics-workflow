# Copyright 2019 Sergio Teruel <sergio.teruel@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Convert invoice_line_id Many2one field to Many2many field if relation
    # table is empty.
    # This is due to a commit from v11 done after v12 migration, so is possible
    # that this field is already converted
    sql = "SELECT COUNT(*) FROM  stock_move_invoice_line_rel;"""
    env.cr.execute(sql)
    if not env.cr.fetchone():
        openupgrade.m2o_to_x2m(env.cr, env['stock.move'], 'stock_move',
                               'invoice_line_ids', 'invoice_line_id')
