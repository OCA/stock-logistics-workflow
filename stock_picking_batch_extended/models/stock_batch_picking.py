# Copyright 2012-2014 Alexandre Fayolle, Camptocamp SA
# Copyright 2018-2020 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models

from odoo.exceptions import UserError


class StockBatchPicking(models.Model):
    """ This object allow to manage multiple stock.picking at the same time.
    """
    # renamed stock.batch.picking -> stock.picking.batch
    _inherit = ['stock.picking.batch', 'mail.thread', 'mail.activity.mixin']
    _name = 'stock.picking.batch'

    name = fields.Char(
        index=True,
        unique=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env['ir.sequence'].next_by_code(
            'stock.picking.batch'
        ),
    )

    # added state to be compatible with picking_ids
    state = fields.Selection(
        selection_add=[
            ('assigned', 'Available'),
        ],
        readonly=True, index=True,
        help='the state of the batch picking. '
             'Workflow is draft -> in_progress/assigned -> done or cancel',
    )

    date = fields.Date(
        string='Date',
        required=True, readonly=True, index=True,
        states={
            'draft': [('readonly', False)],
            'in_progress': [('readonly', False)]
        },
        default=fields.Date.context_today,
        help='date on which the batch picking is to be processed',
    )

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Picker',
        readonly=True, index=True,
        states={
            'draft': [('readonly', False)],
            'in_progress': [('readonly', False)]
        },
        help='the user to which the pickings are assigned',
        old_name='picker_id',
    )

    use_oca_batch_validation = fields.Boolean(
        default=lambda self: self.env.user.company_id.use_oca_batch_validation,
        copy=False,
    )

    picking_ids = fields.One2many(
        string='Pickings',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='List of picking managed by this batch.',
    )
    # TODO add comment to this field
    active_picking_ids = fields.One2many(
        string="Active Pickings",
        comodel_name='stock.picking',
        inverse_name='batch_id',
        readonly=True,
        domain=[('state', 'not in', ('cancel', 'done'))],
    )

    notes = fields.Text('Notes', help='free form remarks')

    move_lines = fields.Many2many(
        comodel_name='stock.move',
        readonly=True,
        string='Operations',
        compute='_compute_move_lines',
    )

    move_line_ids = fields.Many2many(
        comodel_name='stock.move.line',
        string='Detailed operations',
        compute='_compute_move_line_ids',
        # HACK: Allow to write sml fields from this model
        inverse=lambda self: self,
    )

    entire_package_ids = fields.Many2many(
        comodel_name='stock.quant.package',
        compute='_compute_entire_package_ids',
        help='Those are the entire packages of a picking shown in the view of '
             'operations',
    )

    entire_package_detail_ids = fields.Many2many(
        comodel_name='stock.quant.package',
        compute='_compute_entire_package_ids',
        help='Those are the entire packages of a picking shown in the view of '
             'detailed operations',
    )

    picking_count = fields.Integer(
        string='# Pickings',
        compute='_compute_picking_count',
    )

    @api.depends('picking_ids')
    def _compute_move_lines(self):
        for batch in self:
            if batch.use_oca_batch_validation:
                batch.move_lines = batch.picking_ids.mapped("move_lines")

    @api.depends('picking_ids')
    def _compute_move_line_ids(self):
        for batch in self:
            if batch.use_oca_batch_validation:
                batch.move_line_ids = batch.picking_ids.mapped(
                    'move_line_ids'
                )

    @api.depends('picking_ids')
    def _compute_entire_package_ids(self):
        for batch in self:
            if batch.use_oca_batch_validation:
                batch.update({
                    'entire_package_ids': batch.picking_ids.mapped(
                        'entire_package_ids'),
                    'entire_package_detail_ids': batch.picking_ids.mapped(
                        'entire_package_detail_ids'),
                })

    def _compute_picking_count(self):
        """Calculate number of pickings."""
        groups = self.env['stock.picking'].read_group(
            domain=[('batch_id', 'in', self.ids)],
            fields=['batch_id'],
            groupby=['batch_id'],
        )
        counts = {g['batch_id'][0]: g['batch_id_count'] for g in groups}
        for batch in self:
            batch.picking_count = counts.get(batch.id, 0)

    def get_not_empties(self):
        """ Return all batches in this recordset
        for which picking_ids is not empty.

        :raise UserError: If all batches are empty.
        """
        if not self.mapped('picking_ids'):
            if len(self) == 1:
                message = _('This Batch has no pickings')
            else:
                message = _('These Batches have no pickings')

            raise UserError(message)

        return self.filtered(lambda b: len(b.picking_ids) != 0)

    def verify_state(self, expected_state=None):
        """ Check if batches states must be changed based on pickings states.

        If all pickings are canceled, batch must be canceled.
        If all pickings are canceled or done, batch must be done.
        If all pickings are canceled or done or *expected_state*,
            batch must be *expected_state*.

        :return: True if batches states has been changed.
        """
        expected_states = {'done', 'cancel'}
        if expected_state is not None:
            expected_states.add(expected_state)

        all_good = True
        for batch in self.filtered(lambda b: b.state not in expected_states):
            states = set(batch.mapped('picking_ids.state'))
            if not states or states == {'cancel'}:
                batch.state = 'cancel'
            elif states == {'done'} or states == {'done', 'cancel'}:
                batch.state = 'done'

            elif states.issubset(expected_states):
                batch.state = expected_state

            else:
                all_good = False

        return all_good

    @api.multi
    def action_cancel(self):
        """ Call action_cancel for all batches pickings
        and set batches states to cancel too.
        """
        for batch in self:
            if not batch.picking_ids:
                batch.write({'state': 'cancel'})
            else:
                if not batch.verify_state():
                    batch.picking_ids.action_cancel()

    @api.multi
    def action_assign(self):
        """ Check if batches pickings are available.
        """
        batches = self.get_not_empties()
        if not batches.verify_state('in_progress'):
            mass_wiz = self.env['stock.picking.mass.action'].create({
                'check_availability': True,
                'picking_ids': [
                    (6, 0, batches.mapped('active_picking_ids').ids)
                ]
            })
            return mass_wiz.mass_action()

    @api.multi
    def action_transfer(self):
        """ Create wizard to process all active pickings in these batches
        """
        batches = self.get_not_empties()
        if not batches.verify_state():
            mass_wiz = self.env['stock.picking.mass.action'].create({
                'transfer': True,
                'picking_ids': [
                    (6, 0, batches.mapped('active_picking_ids').ids)
                ],
            })
            return mass_wiz.mass_action()

    @api.multi
    def action_print_picking(self):
        pickings = self.mapped('picking_ids')
        if not pickings:
            raise UserError(_('Nothing to print.'))
        return self.env.ref(
            'stock_picking_batch_extended.action_report_batch_picking'
        ).report_action(self)

    @api.multi
    def remove_undone_pickings(self):
        """ Remove of this batch all pickings which state is not done / cancel.
        """
        self.mapped('active_picking_ids').write({'batch_id': False})
        self.verify_state()

    @api.multi
    def action_view_stock_picking(self):
        """This function returns an action that display existing pickings of
        given batch picking.
        """
        self.ensure_one()
        pickings = self.mapped('picking_ids')
        action = self.env.ref('stock.action_picking_tree_all').read([])[0]
        action['domain'] = [('id', 'in', pickings.ids)]
        return action
