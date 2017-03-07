# -*- coding: utf-8 -*-
# © 2012-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockBatchPickingCreator(models.TransientModel):
    """Create a stock.batch.picking from stock.picking
    """

    _name = 'stock.batch.picking.creator'
    _description = 'Batch Picking Creator'

    name = fields.Char(
        'Name', required=True,
        default=lambda x: x.env['ir.sequence'].next_by_code(
            'stock.batch.picking'
        ),
        help='Name of the batch picking'
    )
    date = fields.Date(
        'Date', required=True, select=True, default=fields.Date.context_today,
        help='Date on which the batch picking is to be processed'
    )

    picker_id = fields.Many2one(
        'res.users', string='Picker',
        default=lambda self: self._default_picker_id(),
        help='The user to which the pickings are assigned'
    )

    notes = fields.Text('Notes', help='free form remarks')

    def _default_picker_id(self):
        """ Return default_picker_id from the main company warehouse
        except if a warehouse_id is specified in context.
        """
        warehouse_id = self.env.context.get('warehouse_id')
        if warehouse_id:
            warehouse = self.env['stock.warehouse'].browse(warehouse_id)
        else:
            warehouse = self.env['stock.warehouse'].search([
                ('company_id', '=', self.env.user.company_id.id)
            ], limit=1)

        return warehouse.default_picker_id

    @api.multi
    def action_create_batch(self):
        """ Create a batch picking  with selected pickings after having checked
        that they are not already in another batch or done/cancel.
        """
        pickings = self.env['stock.picking'].search([
            ('id', 'in', self.env.context['active_ids']),
            ('batch_picking_id', '=', False),
            ('state', 'not in', ('cancel', 'done'))
        ])

        if not pickings:
            raise UserError(_(
                "All selected pickings are already in a batch picking "
                "or are in a wrong state."
            ))

        batch = self.env['stock.batch.picking'].create({
            'name': self.name,
            'date': self.date,
            'notes': self.notes,
            'picker_id': self.picker_id.id,
        })

        pickings.write({'batch_picking_id': batch.id})

        return batch.get_formview_action()[0]
