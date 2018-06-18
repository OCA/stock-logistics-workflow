# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class CannabisCannabinoid(models.Model):

    _name = 'cannabis.cannabinoid'
    _description = 'Cannabis Cannabinoid'

    name = fields.Char(
        required=True,
    )

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'This Cannabinoid already exists.'),
    ]

