# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.exceptions import ValidationError


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    automatic_serial_generation = fields.Boolean(
        string=u"Automatic serial generation",
    )

    @api.constrains('automatic_serial_generation', 'tracking')
    def _check_automatic_serial_generation(self):
        for rec in self:
            if rec.automatic_serial_generation and rec.tracking != 'serial':
                raise ValidationError(_(
                    "Automatic serial generation is only available for items "
                    "with a unique serial number tracking"))

    @api.onchange('tracking')
    def _onchange_tracking_auto_serial_generation(self):
        if self.tracking != 'serial' and self.automatic_serial_generation:
            self.automatic_serial_generation = False
