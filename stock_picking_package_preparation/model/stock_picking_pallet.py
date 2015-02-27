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


class StockPickingPallet(models.Model):
    _name = 'stock.picking.pallet'
    _description = 'Prepare Pallet'
    _inherit = ['mail.thread']

    def _default_company_id(self):
        company_model = self.env['res.company']
        return company_model._company_default_get('stock.picking.pallet')

    name = fields.Char(
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
    )
    state = fields.Selection(
        selection=[('draft', 'Draft'),
                   ('cancel', 'Cancelled'),
                   ('done', 'Done'),
                   ],
        default='draft',
        string='State',
        readonly=True,
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        required=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
    )
    picking_ids = fields.Many2many(
        comodel_name='stock.picking',
        string='Transfers',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
    )
    ul_id = fields.Many2one(
        comodel_name='product.ul',
        string='Logistic Unit',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
    )
    packaging_id = fields.Many2one(
        comodel_name='product.packaging',
        string='Packaging',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
    )
    date = fields.Datetime(
        string='Document Date',
        default=fields.Datetime.now,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        select=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        default=_default_company_id,
    )
    pack_operation_ids = fields.One2many(
        comodel_name='stock.pack.operation',
        compute='_compute_pack_operation_ids',
        readonly=True,
    )
    dest_pack_id = fields.Many2one(
        comodel_name='stock.quant.package',
        string='Pack',
        readonly=True,
    )
    note = fields.Text()

    @api.depends('picking_ids',
                 'picking_ids.pack_operation_ids')
    def _compute_pack_operation_ids(self):
        self.pack_operation_ids = self.mapped('picking_ids.pack_operation_ids')

    @api.multi
    def action_done(self):
        self.state = 'done'

    @api.multi
    def action_cancel(self):
        self.state = 'cancel'

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
        self.dest_pack_id = pack.id
        self.picking_ids.do_transfer()

    @api.multi
    def do_generate_pack(self):
        for pallet in self:
            pallet._generate_pack()
        self.action_done()
