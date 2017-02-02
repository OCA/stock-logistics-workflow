# -*- coding: utf-8 -*-
# © 2015-2016 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from . import models


def pre_init_hook(cr):
    query = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name='product_template'
        AND column_name='check_no_negative';
    """
    cr.execute(query)
    if cr.fetchall():
        migrate_from_v8(cr)


def migrate_from_v8(cr):
    """Migration from the v8 version.
    The column has a different name.
    """
    cr.execute("ALTER TABLE product_template "
               "RENAME COLUMN check_no_negative TO allow_negative_stock")
    cr.execute("UPDATE product_template "
               "SET allow_negative_stock = NOT allow_negative_stock")
