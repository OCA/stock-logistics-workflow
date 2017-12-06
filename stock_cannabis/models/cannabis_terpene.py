# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class CannabisTerpene(models.Model):

    _name = 'cannabis.terpene'
    _description = 'Cannabis Terpenes'

    name = fields.Char(
        required=True,
    )
    aroma = fields.Text()
    effects = fields.Text()
    medical_value = fields.Text()

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'This terpene already exists.'),
    ]
