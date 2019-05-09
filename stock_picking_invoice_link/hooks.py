# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID

import logging
_logger = logging.getLogger(__name__)


def link_existing_invoices(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        cr.execute(
            """
            SELECT order_line_id, invoice_line_id
            FROM sale_order_line_invoice_rel
            """
        )
        for sol_id, invl_id in cr.fetchall():
            invls = env['account.invoice.line'].browse(invl_id)
            sol = env['sale.order.line'].browse(sol_id)
            inv = invls.mapped('invoice_id')
            sol.mapped(
                'procurement_ids'
            ).mapped(
                'move_ids'
            ).filtered(
                lambda x: x.state == 'done' and
                not x.location_dest_id.scrap_location and
                x.location_dest_id.usage == 'customer'
            ).mapped(
                'picking_id'
            ).write({'invoice_ids': [(4, inv.ids)]})
            _logger.info('Picking %s assigned to %s' % (sol.mapped(
                'procurement_ids'
            ).mapped(
                'move_ids'
            ).filtered(
                lambda x: x.state == 'done' and
                not x.location_dest_id.scrap_location and
                x.location_dest_id.usage == 'customer'
            ).mapped(
                'picking_id.name'
            ), inv.number))
            sol.mapped('procurement_ids').mapped('move_ids').write(
                {'invoice_line_id': invl_id})
