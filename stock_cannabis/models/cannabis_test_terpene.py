# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class CannabisTestTerpene(models.Model):

    _name = 'cannabis.test.terpene'
    _inherit = 'cannabis.test.result'
    _description = 'Cannabis Test Terpenes'

    terpene_id = fields.Many2one(
        string='Terpene',
        comodel_name='cannabis.terpene'
    )

    def _compute_name(self):
        for record in self:
            record.name = '%s - %s %s/%s' % (
                record.terpene_id.name,
                record.quantity_reduced,
                record.quantity_uom_id.name,
                record.test_quantity_uom_id.name,
            )
