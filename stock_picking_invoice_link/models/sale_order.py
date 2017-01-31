# -*- coding: utf-8 -*-
# © 2013-15 Agile Business Group sagl (<http://www.agilebg.com>)
# © 2017 Jacques-Etienne Baudoux <je@bcim.be>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def invoice_line_create(self, invoice_id, qty):
        res = super(SaleOrderLine, self).invoice_line_create(invoice_id, qty)
        self.mapped('procurement_ids') \
            .mapped('move_ids') \
            .filtered(
                lambda x: x.state == 'done' and
                not x.location_dest_id.scrap_location and
                x.location_dest_id.usage == 'customer') \
            .mapped('picking_id') \
            .write({'invoice_id': invoice_id})
        return res

    @api.multi
    def _prepare_invoice_line(self, qty):
        vals = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        # move_ids = self.procurement_ids.mapped('move_ids').filtered(
        #     lambda x: x.state == 'done' and
        #     not x.location_dest_id.scrap_location and
        #     x.location_dest_id.usage == 'customer').ids

        # For performance reason, we compute the list of move in SQL
        self._cr.execute("""
            SELECT stock_move.id FROM stock_move
            LEFT JOIN stock_location
                ON stock_location.id=stock_move.location_dest_id
            LEFT JOIN procurement_order
                ON procurement_order.id=stock_move.procurement_id
            LEFT JOIN sale_order_line
                ON sale_order_line.id=procurement_order.sale_line_id
            WHERE stock_move.state='done'
                AND stock_location.scrap_location != 't'
                AND stock_location.usage = 'customer'
                AND sale_order_line.id in %s
            """, (tuple(self.ids),))

        move_ids = [row[0] for row in self._cr.fetchall()]
        vals['move_line_ids'] = [(6, 0, move_ids)]
        return vals
