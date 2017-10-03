# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.exceptions import ValidationError


class StockPickingType(models.Model):

    _inherit = 'stock.picking.type'

    automatic_serial_generation = fields.Boolean(
        string=u"Automatic serial generation",
        copy=False,
    )

    @api.constrains('automatic_serial_generation', 'code')
    def _check_automatic_serial_generation(self):
        for rec in self:
            if rec.automatic_serial_generation and rec.code != 'incoming':
                raise ValidationError(_(
                    "The automatic serial generation is available only for "
                    "operations with type supplier."))

    @api.onchange('automatic_serial_generation')
    def _onchange_automatic_serial_generation(self):
        """ if `automatic_serial_generation` is checked make sure the
        `use_create_lots` is also checked. The `use_create_lots` is meant
        to force the creation of a lot/serial every time a lot/serial number
        is provided.
        """
        if self.automatic_serial_generation:
            self.use_create_lots = True
            self.use_existing_lots = False
        return {}
