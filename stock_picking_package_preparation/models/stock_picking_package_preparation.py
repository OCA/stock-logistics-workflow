# -*- coding: utf-8 -*-
# Copyright 2015 Guewen Baconnier
# Copyright 2016 Lorenzo Battistini - Agile Business Group
# Copyright 2016 Alessio Gerace - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import Warning as UserError


class StockPickingPackagePreparation(models.Model):
    _name = 'stock.picking.package.preparation'
    _description = 'Package Preparation'
    _inherit = ['mail.thread']

    FIELDS_STATES = {'done': [('readonly', True)],
                     'in_pack': [('readonly', True)],
                     'cancel': [('readonly', True)]}

    def _default_company_id(self):
        company_model = self.env['res.company']
        return company_model._company_default_get(self._name)

    name = fields.Char(
        related='package_id.name',
        readonly=True,
        index=True,
        store=True,
    )
    state = fields.Selection(
        selection=[('draft', 'Draft'),
                   ('cancel', 'Cancelled'),
                   ('in_pack', 'In Pack'),
                   ('done', 'Done'),
                   ],
        default='draft',
        string='State',
        readonly=True,
        copy=False,
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        required=True,
        states=FIELDS_STATES,
    )
    picking_ids = fields.Many2many(
        comodel_name='stock.picking',
        relation='stock_picking_pack_prepare_rel',
        column1='stock_picking_package_preparation_id',
        column2='stock_picking_id',
        string='Transfers',
        copy=False,
        states=FIELDS_STATES,
    )
    packaging_id = fields.Many2one(
        comodel_name='product.packaging',
        string='Packaging',
        states=FIELDS_STATES,
    )
    date = fields.Datetime(
        string='Document Date',
        default=fields.Datetime.now,
        states=FIELDS_STATES,
    )
    date_done = fields.Datetime(
        string='Shipping Date',
        readonly=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        index=True,
        states=FIELDS_STATES,
        default=_default_company_id,
    )
    pack_operation_ids = fields.One2many(
        comodel_name='stock.pack.operation',
        compute='_compute_pack_operation_ids',
        readonly=True,
    )
    package_id = fields.Many2one(
        comodel_name='stock.quant.package',
        string='Pack',
        readonly=True,
        copy=False,
    )
    note = fields.Text()
    weight = fields.Float(compute='_compute_weight',
                          help="The weight is computed when the "
                               "preparation is done.")
    quant_ids = fields.Many2many(
        compute='_compute_quant_ids',
        comodel_name='stock.quant',
        relation='stock_quant_pack_prepare_rel',
        column1='stock_picking_package_preparation_id',
        column2='stock_quant_id',
        string='All Content',
    )

    @api.multi
    @api.depends('package_id',
                 'package_id.children_ids')
    def _compute_quant_ids(self):
        for preparation in self:
            package = preparation.package_id
            preparation.quant_ids = package.get_content()

    @api.multi
    @api.depends('package_id',
                 'package_id.children_ids',
                 'package_id.quant_ids')
    def _compute_weight(self):
        for preparation in self:
            package = preparation.package_id
            if not package:
                return
            quants = package.get_content()
            # weight of the products only
            weight = sum(l.product_id.weight * l.qty for l in quants)
            preparation.weight = weight

    @api.multi
    @api.depends('picking_ids',
                 'picking_ids.pack_operation_ids')
    def _compute_pack_operation_ids(self):
        for preparation in self:
            preparation.pack_operation_ids = preparation.mapped(
                'picking_ids.pack_operation_ids')

    @api.multi
    def action_done(self):
        if not self.mapped('package_id'):
            raise UserError(
                _('The package has not been generated.')
            )
        for picking in self.picking_ids:
            picking.do_transfer()
        self.write({'state': 'done', 'date_done': fields.Datetime.now()})

    @api.multi
    def action_cancel(self):
        if any(prep.state == 'done' for prep in self):
            raise UserError(
                _('Cannot cancel a done package preparation.')
            )
        package_ids = self.mapped('package_id')
        if package_ids:
            package_ids.unlink()
        self.write({'state': 'cancel'})

    @api.multi
    def action_draft(self):
        if any(prep.state != 'cancel' for prep in self):
            raise UserError(
                _('Only canceled package preparations can be reset to draft.')
            )
        self.write({'state': 'draft'})

    @api.multi
    def action_put_in_pack(self):
        for preparation in self:
            preparation._generate_pack()
        self.write({'state': 'in_pack'})

    @api.multi
    def _prepare_package(self):
        self.ensure_one()
        if not self.picking_ids:
            raise UserError(
                _('No transfer selected for this preparation.')
            )
        location = self.mapped('picking_ids.location_dest_id')
        if len(location) > 1:
            raise UserError(
                _('All the transfers must have the same destination location')
            )
        values = {
            'packaging_id': self.packaging_id.id,
            'location_id': location.id,
        }
        return values

    @api.multi
    def _generate_pack(self):
        self.ensure_one()
        pack_model = self.env['stock.quant.package']
        moves = self.env['stock.move']
        operation_model = self.env['stock.pack.operation']

        if any(picking.state != 'assigned' for picking in self.picking_ids):
            raise UserError(
                _('All the transfers must be "Ready to Transfer".')
            )

        operations = operation_model.browse()
        for picking in self.picking_ids:
            if not picking.pack_operation_ids:
                picking.do_prepare_partial()
            operations |= picking.pack_operation_ids

        for operation in operations:
            for record in operation.linked_move_operation_ids:
                moves |= record.move_id
            for move in moves:
                moves.check_tracking(operation)

            operation.qty_done = operation.product_qty

        pack = pack_model.create(self._prepare_package())

        operations.write({'result_package_id': pack.id})
        self.package_id = pack.id
