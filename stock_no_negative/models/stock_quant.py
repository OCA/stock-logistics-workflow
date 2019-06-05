# © 2015-2017 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, _
from odoo.exceptions import ValidationError
from odoo.tools import config, float_compare


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.multi
    @api.constrains('product_id', 'quantity')
    def check_negative_qty(self):
        p = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        check_negative_qty = (
            (config['test_enable'] and
             self.env.context.get('test_stock_no_negative')) or
            not config['test_enable']
        )
        if not check_negative_qty:
            return

        for quant in self:
            disallowed_by_product = \
                not quant.product_id.allow_negative_stock \
                and not quant.product_id.categ_id.allow_negative_stock
            disallowed_by_location = not quant.location_id.allow_negative_stock
            if (
                float_compare(quant.quantity, 0, precision_digits=p) == -1 and
                quant.product_id.type == 'product' and
                quant.location_id.usage in ['internal', 'transit'] and
                disallowed_by_product and disallowed_by_location
            ):
                msg_add = ''
                if quant.lot_id:
                    # Now find a quant we can compensate the negative quants
                    #  with some untracked quants.
                    untracked_qty = quant._get_available_quantity(
                        quant.product_id, quant.location_id, lot_id=False,
                        strict=True)
                    if float_compare(abs(quant.quantity),
                                     untracked_qty, precision_digits=p) < 1:
                        return True
                    msg_add = _(" lot '%s'") % quant.lot_id.display_name
                raise ValidationError(_(
                    "You cannot validate this stock operation because the "
                    "stock level of the product '%s'%s would become negative "
                    "(%s) on the stock location '%s' and negative stock is "
                    "not allowed for this product and/or location.") % (
                        quant.product_id.name, msg_add, quant.quantity,
                        quant.location_id.complete_name))
