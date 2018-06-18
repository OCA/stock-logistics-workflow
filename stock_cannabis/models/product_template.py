# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    cannabis_strain_id = fields.Many2one(
        string='Cannabis Strain',
        comodel_name='cannabis.strain',
    )
