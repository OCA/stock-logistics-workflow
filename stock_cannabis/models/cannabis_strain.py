# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models


class CannabisStrain(models.Model):

    _name = 'cannabis.strain'
    _description = 'Cannabis Strain'

    code = fields.Char()
    name = fields.Char(
        required=True,
    )
