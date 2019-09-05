# Copyright (C) 2018 Akretion (<http://www.akretion.com>)
# @author: Florian da Costa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    allow_whole_order_dropshipping = fields.Boolean(
        string="Overall Dropshipping",
        help="If checked and at least one dropshipping product required "
             "for a sale,\nwhole furnitures of this vendor will be "
             "delivered in dropshipping flow whether routes "
             "defined in product.")
