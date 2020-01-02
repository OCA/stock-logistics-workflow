# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    display_use_date_at_lot_creation = fields.Boolean(
        string="Enter 'Best before Date' date at lot creation",
        help="If this is checked, you will be able to enter a 'Best before "
             "date' on the stock move lines before the creation of new "
             "Lots/Serial Numbers."
    )
