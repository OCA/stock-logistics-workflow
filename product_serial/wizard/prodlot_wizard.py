# -*- coding: utf-8 -*-
##############################################################################
#
#    Product serial module for Odoo
#    Copyright (C) 2010 NaN Projectes de Programari Lliure, S.L.
#                       http://www.NaN-tic.com
#    Copyright (C) 2013-2015 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError
import base64


class StockProdlotSelection(models.TransientModel):
    _name = 'stock.prodlot.selection'
    _description = "Select or Create Production Lots"

    product_id = fields.Many2one(
        'product.product', string='Product', required=True)
    prefix = fields.Char(string='Prefix')
    suffix = fields.Char(string='Suffix')
    first_number = fields.Char(string='First Number')
    last_number = fields.Char(string='Last Number')
    prodlot_file = fields.Binary(
        string='Serial Numbers File',
        help="The serial numbers file should be a text file with one line "
        "per serial number (all for the same product).")
    create_prodlots = fields.Boolean(string='Create New Serial Numbers')

    @api.model
    def default_get(self, fields):
        res = super(StockProdlotSelection, self).default_get(fields)
        trf = self._get_transfer()
        if trf.picking_id.picking_type_id.code == 'incoming':
            res['create_prodlots'] = True
        return res

    @api.model
    def _get_transfer(self):
        assert ('active_id' in self._context),\
            "Missing 'active_id' key in context"
        assert self._context['active_model'] == 'stock.transfer_details',\
            "Active model should be stock.transfer_details"
        transfer = self.env['stock.transfer_details'].browse(
            self._context['active_id'])
        return transfer

    @api.multi
    def select_or_create_prodlots_from_file(self):
        self.ensure_one()

        if not self.prodlot_file:
            raise UserError(_(
                "You should upload a text file containing the serial "
                "numbers."))
        full_prodlot_str = base64.decodestring(self.prodlot_file)
        full_prodlot_seq = full_prodlot_str.splitlines()
        # Remove empty lines
        prodlot_seq = [prodlot for prodlot in full_prodlot_seq if prodlot]
        transfer = self._get_transfer()
        return self._select_or_create_prodlots(
            transfer, self.product_id, prodlot_seq, self.create_prodlots)

    @api.multi
    def select_or_create_prodlots_from_interval(self):
        self.ensure_one()
        prefix = self.prefix or ''
        suffix = self.suffix or ''
        if not self.first_number or not self.last_number:
            raise UserError(_(
                "You should enter a value for the First Number and the "
                "Last Number"))
        try:
            first_number = int(self.first_number)
        except:
            raise UserError(_(
                "The field 'First Number' should only contain digits."))

        try:
            last_number = int(self.last_number)
        except:
            raise UserError(_(
                "The field 'Last Number' should only contain digits."))

        if int(self.first_number) <= 0 or int(self.last_number) <= 0:
            raise UserError(_(
                "The First and Last Numbers should be strictly positive."))

        if last_number < first_number:
            raise UserError(_(
                'The First Number must be lower than the Last Number.'))

        if len(self.first_number) != len(self.last_number):
            raise UserError(_(
                'First and Last Numbers must have the same length.'))

        number_length = len(self.first_number)
        prodlot_seq = [
            '%s%0*d%s' % (prefix, number_length, current_number, suffix)
            for current_number in range(first_number, last_number+1)
            ]
        transfer = self._get_transfer()
        return self._select_or_create_prodlots(
            transfer, self.product_id, prodlot_seq, self.create_prodlots)

    @api.model
    def _prepare_prodlot(self, product, lot_name):
        '''This method is designed to be inherited'''
        return {
            'product_id': product.id,
            'name': lot_name,
        }

    @api.model
    def _select_or_create_prodlots(
            self, transfer, product, prodlot_seq, create_prodlots):
        assert prodlot_seq and isinstance(prodlot_seq, list),\
            'wrong prodlot_seq'
        splo = self.env['stock.production.lot']
        for transfer_item in transfer.item_ids:
            if transfer_item.product_id != product:
                continue
            try:
                current_lot = prodlot_seq.pop(0)
            except:
                break
            if create_prodlots:
                # Create new prodlot
                lot = splo.create(self._prepare_prodlot(product, current_lot))
            else:
                # Search existing prodlots
                lots = splo.search([
                    ('name', '=', current_lot),
                    ('product_id', '=', product.id),
                    ], limit=1)
                if not lots:
                    raise UserError(_(
                        "Serial Number '%s' not found for product '%s'.")
                        % (current_lot,
                           transfer_item.product_id.name_get()[0][1]))
                lot = lots[0]

            transfer_item.lot_id = lot.id
        return transfer.wizard_view()

    @api.multi
    def cancel(self):
        """We have to re-call the wizard when the user clicks on Cancel"""
        self.ensure_one()
        assert self.env.context.get('active_model') == \
            'stock.transfer_details', 'Wrong underlying model'
        trf = self.env['stock.transfer_details'].browse(
            self.env.context['active_id'])
        action = trf.wizard_view()
        return action
