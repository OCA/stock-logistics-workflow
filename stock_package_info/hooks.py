# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.

from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    """Enable packaging options in stock config & migrate dimensions."""

    # cr.execute("UPDATE product_packaging "
    #            "SET length_float = product_packaging.length, "
    #            "    width_float = product_packaging.width, "
    #            "    height_float = product_packaging.height")

    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        wizard = env['stock.config.settings'].create({
            'group_stock_tracking_lot': 1,
        })
        wizard.execute()


def uninstall_hook(cr, registry):
    """Convert the float package dimensions to int."""
    cr.execute("UPDATE product_packaging "
               "SET length = product_packaging.length_float, "
               "    width = product_packaging.width_float, "
               "    height = product_packaging.height_floatpicking")
