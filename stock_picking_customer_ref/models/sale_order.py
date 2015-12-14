# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def write(self, vals):
        picking_obj = self.env['stock.picking']
        res = super(SaleOrder, self).write(vals)
        # The field "client_order_ref" of pickings, is a calculated field. It
        # can not be put into the field dependence "sale_id".
        for sale in self:
            if (vals.get('client_order_ref', False) and
                    sale.procurement_group_id):
                cond = [('group_id', '=', sale.procurement_group_id.id)]
                pickings = picking_obj.search(cond)
                pickings.write({'client_order_ref':
                                vals.get('client_order_ref')})
        return res
