# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockChangeStandardPrice(models.TransientModel):

    _inherit = 'stock.change.standard.price'

    date = fields.Date(
        help="The date used to create account moves. If empty, assumes today."
             "Cannot be a date in the future."
    )

    @api.multi
    def _get_check_product_moves_dates(self):
        """
        If there are account moves for the product with date > the wizard date,
        we don't change the product standard price
        :return: a recordset with records that don't need to change price
        """
        if self.date and self.date != fields.Date.today():
            return True
        return False

    @api.multi
    def change_price(self):
        self_with_context = self.with_context(
            move_date=self.date,
            check_product_moves_date=self._get_check_product_moves_dates()
        )
        return super(
            StockChangeStandardPrice, self_with_context).change_price()

    @api.constrains('date')
    def _constrains_date(self):
        for wizard in self:
            if wizard.date and wizard.date > fields.Date.today():
                raise ValidationError(
                    _('The chosen date should be today or in the past!'))
