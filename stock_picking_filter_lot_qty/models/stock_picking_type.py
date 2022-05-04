from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    use_available_lots = fields.Boolean(
        help="Extends the Use existing lots option by filtering only those with "
             "available quantity."
    )
    use_location_lots = fields.Boolean(
        help="Filters only the lots on origin location and its children."
    )

    @api.onchange('use_available_lots')
    def onchange_use_available_lots(self):
        if self.use_available_lots:
            self.use_existing_lots = True

    @api.multi
    @api.constrains('use_available_lots', 'use_existing_lots')
    def check_available_lots(self):
        for record in self:
            if record.use_available_lots and not record.use_existing_lots:
                raise ValidationError(_(
                    "Use available lots can be activated only if Use existing lots is "
                    "enabled."
                ))
