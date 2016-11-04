# -*- coding: utf-8 -*-
# © 2016 Sergio Teruel <sergio.teruel@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from . import models
from . import wizards

from openerp import api, SUPERUSER_ID


def post_init_hook(cr, pool):
    """On first install of the module, this method is called to create a
    deposit location per warehouse.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})

    warehouses = env['stock.warehouse'].search([])
    for warehouse in warehouses:
        warehouse._create_deposit_values()
