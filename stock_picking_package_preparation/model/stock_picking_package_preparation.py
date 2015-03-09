# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2015 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, exceptions, _


class StockPickingPackagePreparation(models.Model):
    _name = 'stock.picking.package.preparation'
    _description = 'Package Preparation'
    _inherit = ['mail.thread']

    def _default_company_id(self):
        company_model = self.env['res.company']
        return company_model._company_default_get(self._name)

    name = fields.Char(
        related='package_id.name',
        readonly=True,
        select=True,
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
        states={'done': [('readonly', True)],
                'in_pack': [('readonly', True)],
                'cancel': [('readonly', True)]},
    )
    picking_ids = fields.Many2many(
        comodel_name='stock.picking',
        string='Transfers',
        copy=False,
        states={'done': [('readonly', True)],
                'in_pack': [('readonly', True)],
                'cancel': [('readonly', True)]},
    )
    ul_id = fields.Many2one(
        comodel_name='product.ul',
        string='Logistic Unit',
        states={'done': [('readonly', True)],
                'in_pack': [('readonly', True)],
                'cancel': [('readonly', True)]},
    )
    packaging_id = fields.Many2one(
        comodel_name='product.packaging',
        string='Packaging',
        states={'done': [('readonly', True)],
                'in_pack': [('readonly', True)],
                'cancel': [('readonly', True)]},
    )
    date = fields.Datetime(
        string='Document Date',
        default=fields.Datetime.now,
        states={'done': [('readonly', True)],
                'in_pack': [('readonly', True)],
                'cancel': [('readonly', True)]},
    )
    date_done = fields.Datetime(
        string='Shipping Date',
        readonly=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        select=True,
        states={'done': [('readonly', True)],
                'in_pack': [('readonly', True)],
                'cancel': [('readonly', True)]},
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
    weight = fields.Float(compute='_compute_weight')
    net_weight = fields.Float(compute='_compute_weight')
    quant_ids = fields.Many2many(
        compute='_compute_quant_ids',
        comodel_name='stock.quant',
        name='All Content',
    )

    @api.one
    @api.depends('package_id',
                 'package_id.children_ids')
    def _compute_quant_ids(self):
        package = self.package_id
        quants = self.env['stock.quant'].browse(package.get_content())
        self.quant_ids = quants

    @api.one
    @api.depends('package_id',
                 'package_id.children_ids',
                 'package_id.ul_id',
                 'package_id.quant_ids')
    def _compute_weight(self):
        package = self.package_id
        quant_model = self.env['stock.quant']
        package_model = self.env['stock.quant.package']
        quants = quant_model.browse(package.get_content())
        # weight of the products only
        net_weight = sum(l.product_id.weight * l.qty for l in quants)
        # weight of the empty packages + products
        child_packages = package_model.search([('id', 'child_of', package.id)])
        weight = sum(child_packages.mapped('ul_id.weight')) + net_weight
        self.net_weight = net_weight
        self.weight = weight

    @api.depends('picking_ids',
                 'picking_ids.pack_operation_ids')
    def _compute_pack_operation_ids(self):
        self.pack_operation_ids = self.mapped('picking_ids.pack_operation_ids')

    @api.multi
    def action_done(self):
        if not self.package_id:
            raise exceptions.Warning(
                _('The package has not been generated.')
            )
        self.picking_ids.do_transfer()
        self.write({'state': 'done', 'date_done': fields.Datetime.now()})

    @api.multi
    def action_cancel(self):
        if self.state == 'done':
            raise exceptions.Warning(
                _('Cannot cancel a done package preparation.')
            )
        if self.package_id:
            self.package_id.unlink()
        self.state = 'cancel'

    @api.multi
    def action_draft(self):
        if self.state != 'cancel':
            raise exceptions.Warning(
                _('Only canceled package preparations can be reset to draft.')
            )
        self.state = 'draft'

    @api.multi
    def action_put_in_pack(self):
        for preparation in self:
            preparation._generate_pack()
        self.state = 'in_pack'

    @api.multi
    def _prepare_package(self):
        location = self.mapped('picking_ids.location_dest_id')
        if len(location) != 1:
            raise exceptions.Warning(
                _('All the transfers must have the same destination location')
            )
        values = {
            'packaging_id': self.packaging_id.id,
            'ul_id': self.ul_id.id,
            'location_id': location.id,
        }
        return values

    @api.multi
    def _generate_pack(self):
        self.ensure_one()
        pack_model = self.env['stock.quant.package']
        move_model = self.env['stock.move']
        operation_model = self.env['stock.pack.operation']

        if any(picking.state != 'assigned' for picking in self.picking_ids):
            raise exceptions.Warning(
                _('All the transfers must be "Ready to Transfer".')
            )

        operations = operation_model.browse()
        for picking in self.picking_ids:
            if not picking.pack_operation_ids:
                picking.do_prepare_partial()
            operations |= picking.pack_operation_ids

        for operation in operations:
            if (operation.product_id and
                    operation.location_id and
                    operation.location_dest_id):
                move_model.check_tracking_product(
                    operation.product_id,
                    operation.lot_id.id,
                    operation.location_id,
                    operation.location_dest_id
                )
            operation.qty_done = operation.product_qty

        pack = pack_model.create(self._prepare_package())

        operations.write({'result_package_id': pack.id})
        self.package_id = pack.id
