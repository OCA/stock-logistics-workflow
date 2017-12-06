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
    parent_ids = fields.Many2many(
        string='Parents',
        comodel_name=_name,
    )
    child_ids = fields.Many2many(
        string='Children',
        comodel_name=_name,
        compute='_compute_child_ids',
    )

    @api.multi
    def _compute_child_ids(self):
        for record in self:
            record.child_ids = self.search([
                ('parent_ids', 'in', self.ids),
            ])
