# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID
from odoo.api import Environment


def post_init_hook(cr, pool):
    """
    Fetches all the pickings and resets the sequence of the move lines
    """
    env = Environment(cr, SUPERUSER_ID, {})
    stock = env['stock.picking'].search([])
    stock._reset_sequence()
