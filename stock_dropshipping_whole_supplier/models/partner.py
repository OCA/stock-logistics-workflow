# -*- coding: utf-8 -*-
# Copyright (C) 2018 Akretion (<http://www.akretion.com>)
# @author: Florian da Costa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    allow_whole_order_dropshipping = fields.Boolean(
		help="In this cas, if at least one product is configured with"
			 "drop shipping route in a sale order for this supplier, all the"
			 " other products of the sale order will be delivered in "
			 "drop shipping")
