# Copyright 2012-2016 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import json
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockBatchPickingCreator(models.TransientModel):
    """Create a stock.picking.batch from stock.picking
    """

    _name = 'stock.picking.batch.creator'
    _description = 'Batch Picking Creator'
    _group_field_param = 'stock_batch_picking.group_field'

    name = fields.Char(
        'Name', required=True,
        default=lambda x: x.env['ir.sequence'].next_by_code(
            'stock.picking.batch'
        ),
        help='Name of the batch picking'
    )
    date = fields.Date(
        'Date', required=True, index=True, default=fields.Date.context_today,
        help='Date on which the batch picking is to be processed'
    )

    user_id = fields.Many2one(
        'res.users', string='Picker',
        oldname='picker_id',
        default=lambda self: self._default_user_id(),
        help='The user to which the pickings are assigned',
    )
    notes = fields.Text('Notes', help='free form remarks')
    batch_by_group = fields.Boolean(
        string='Create batch pickings grouped by fields',
    )
    group_field_ids = fields.One2many(
        comodel_name='stock.picking.batch.creator.group.field',
        inverse_name='batch_picking_creator_id',
        string='Group by field',
        help='If set any, multiple batch picking will be created, one per '
             'group field',
    )

    @api.onchange('batch_by_group')
    def onchange_batch_by_group(self):
        if self.batch_by_group:
            self.group_field_ids = False
            for index, field in enumerate(self.load_store_fields()):
                self.group_field_ids += self.group_field_ids.new({
                    'sequence': index,
                    'field_id': field.id,
                })

    def load_store_fields(self):
        group_field_ids = self.env['ir.config_parameter'].sudo().get_param(
            self._group_field_param)
        group_fields = self.env['ir.model.fields'].browse(
            group_field_ids and json.loads(group_field_ids))
        return group_fields

    @api.model
    def default_get(self, fields):
        """
        Set last grouped fields used that are stored in config parameters
        """
        res = super().default_get(fields)
        group_fields = self.load_store_fields()
        res['batch_by_group'] = group_fields and True or False
        return res

    def _default_user_id(self):
        """ Return default_user_id from the main company warehouse
        except if a warehouse_id is specified in context.
        """
        warehouse_id = self.env.context.get('warehouse_id')
        if warehouse_id:
            warehouse = self.env['stock.warehouse'].browse(warehouse_id)
        else:
            warehouse = self.env['stock.warehouse'].search([
                ('company_id', '=', self.env.user.company_id.id)
            ], limit=1)

        return warehouse.default_user_id

    def _prepare_stock_batch_picking(self):
        return {
            'name': self.name,
            'date': self.date,
            'notes': self.notes,
            'user_id': self.user_id.id,
        }

    def _raise_message_error(self):
        return _(
            "All selected pickings are already in a batch picking "
            "or are in a wrong state."
        )

    def create_simple_batch(self, domain):
        """ Create one batch picking with all pickings """
        pickings = self.env['stock.picking'].search(domain)
        if not pickings:
            raise UserError(self._raise_message_error())
        batch = self.env['stock.picking.batch'].create(
            self._prepare_stock_batch_picking())
        pickings.write({'batch_id': batch.id})
        return batch

    def create_multiple_batch(self, domain):
        """ Create n batch pickings by grouped fields selected """
        StockPicking = self.env['stock.picking']
        groupby = [f.field_id.name for f in self.group_field_ids]
        pickings_grouped = StockPicking.read_group(domain, groupby, groupby)
        if not pickings_grouped:
            raise UserError(self._raise_message_error())
        batchs = self.env['stock.picking.batch'].browse()
        for group in pickings_grouped:
            batchs += self.env['stock.picking.batch'].create(
                self._prepare_stock_batch_picking())
            StockPicking.search(group['__domain']).write({
                'batch_id': batchs[-1:].id,
            })
        return batchs

    @api.multi
    def action_create_batch(self):
        """ Create a batch picking  with selected pickings after having checked
        that they are not already in another batch or done/cancel.
        """
        domain = [
            ('id', 'in', self.env.context['active_ids']),
            ('batch_id', '=', False),
            ('state', 'not in', ('cancel', 'done')),
        ]
        if self.batch_by_group and self.group_field_ids:
            batchs = self.create_multiple_batch(domain)
        else:
            batchs = self.create_simple_batch(domain)

        # Store as system parameter the fields used to be loaded in the next
        # execution keeping the order.
        if self.batch_by_group:
            group_fields = [f.field_id.id for f in self.group_field_ids]
            self.env["ir.config_parameter"].sudo().set_param(
                self._group_field_param, group_fields)
        return self.action_view_batch_picking(batchs)

    @api.multi
    def action_view_batch_picking(self, batch_pickings):
        if len(batch_pickings) > 1:
            action = self.env.ref(
                'stock_picking_batch_oca.action_stock_batch_picking_tree'
            ).read()[0]
            action['domain'] = [('id', 'in', batch_pickings.ids)]
        else:
            action = batch_pickings.get_formview_action()
        return action


class StockBatchPickingCreatorGroupField(models.TransientModel):
    """ Make mass batch pickings from grouped fields """
    _name = 'stock.picking.batch.creator.group.field'
    _description = 'Batch Picking Creator Group Field'
    _order = 'sequence, id'

    batch_picking_creator_id = fields.Many2one(
        comodel_name='stock.picking.batch.creator',
        ondelete="cascade",
        required=True,
    )
    sequence = fields.Integer(help='Group by picking field')
    field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Field to group',
        domain=[
            ('model', '=', 'stock.picking'),
            ('store', '=', True),
        ],
        required=True,
    )
