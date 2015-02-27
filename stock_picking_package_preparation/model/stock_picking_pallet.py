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

from openerp import models, fields, api


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
        related='picking_ids.pack_operation_ids',
        readonly=True,
    )
    dest_pack_id = fields.Many2one(
        comodel_name='stock.quant.package',
        string='Pack',
        readonly=True,
    )
    note = fields.Text()

    @api.multi
    def action_done(self):
        self.state = 'done'

    @api.multi
    def action_cancel(self):
        self.state = 'cancel'

    @api.multi
    def generate_pack(self):
        # TODO generate the pack, confirm the pickings
        self.action_done()
