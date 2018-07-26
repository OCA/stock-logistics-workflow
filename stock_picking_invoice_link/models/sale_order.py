# Copyright 2013-15 Agile Business Group sagl (<http://www.agilebg.com>)
# Copyright 2017 Jacques-Etienne Baudoux <je@bcim.be>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def invoice_line_create(self, invoice_id, qty):
        self.mapped(
            'move_ids'
        ).filtered(
            lambda x: x.state == 'done' and
            not x.invoice_line_id and
            not x.location_dest_id.scrap_location and
            x.location_dest_id.usage == 'customer'
        ).mapped(
            'picking_id'
        ).write({'invoice_ids': [(4, invoice_id)]})
        return super(SaleOrderLine, self).invoice_line_create(invoice_id, qty)

    @api.multi
    def _prepare_invoice_line(self, qty):
        vals = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        move_ids = self.mapped('move_ids').filtered(
            lambda x: x.state == 'done' and
            not x.invoice_line_id and
            not x.scrapped and (
                x.location_dest_id.usage == 'customer' or
                (x.location_id.usage == 'customer' and
                 x.to_refund)
            )).ids
        vals['move_line_ids'] = [(6, 0, move_ids)]
        return vals
