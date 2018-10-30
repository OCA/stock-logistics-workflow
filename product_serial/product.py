# -*- coding: utf-8 -*-
# © 2008 Raphaël Valyi
# © 2013-2015 Akretion (http://www.akretion.com/) - Alexis de Lattre
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    lot_split_type = fields.Selection([
        ('none', 'None'),
        ('single', 'Single'),
        # ('lu', 'Logistical Unit')  # TODO : restore if someone needs it
        # and implement it properly ('lu' was not fully implemented in v7)
        ], string='Lot split type', default='none',
        help="You should select 'Single' if you have one serial number per "
        "item. In this case, the Transfer pop-up on the picking will "
        "display one line per unit for this product. "
        "The default value is 'None': for those product, the native "
        "process is not modified.")
