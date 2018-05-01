# -*- coding: utf-8 -*-
#    Copyright (C) Rooms For (Hong Kong) Limited T/A OSCG
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

from openerp.osv import osv
import logging
_logger = logging.getLogger(__name__)


class stock_quant(osv.osv):
    _inherit = "stock.quant"

    """
    Following method is a copy from the official Odoo branch
    (addons/stock_account/stock_account.py) with only change on the condition
    where judgment on quant's owner is made (see lines with comment
    "REPLACED").
    This is due to the fact that this module makes the owner_id a required
    field regardless of who owns the stock, while standard Odoo assumes the
    field should be blank in case the stock is owned by the company.
    As this overrides the original method, the content may need to be
    backported from the official branch as necessary.
    """
    def _account_entry_move(self, cr, uid, quants, move, context=None):
        """
        Accounting Valuation Entries

        quants: browse record list of Quants to create accounting valuation
            entries for. Unempty and all quants are supposed to have the same
            location id (thay already moved in)
        move: Move to use. browse record
        """
        if context is None:
            context = {}
        location_obj = self.pool.get('stock.location')
        location_from = move.location_id
        location_to = quants[0].location_id
        company_from = location_obj._location_owner(cr, uid, location_from,
            context=context)
        company_to = location_obj._location_owner(cr, uid, location_to,
            context=context)

        if move.product_id.valuation != 'real_time':
            return False
        for q in quants:
            # if q.owner_id:  # REPLACED
            if q.owner_id and q.owner_id != q.company_id.partner_id:
                # if the quant isn't owned by the company, we don't make any 
                # valuation entry
                return False
            if q.qty <= 0:
                # we don't make any stock valuation for negative quants
                # because the valuation is already made for the counterpart.
                # At that time the valuation will be made at the product cost
                # price and afterward there will be new accounting entries
                # to make the adjustments when we know the real cost price.
                return False

        # in case of routes making the link between several warehouse of the
        # same company, the transit location belongs to this company, so we
        # don't need to create accounting entries
        # Create Journal Entry for products arriving in the company
        if company_to and (move.location_id.usage not in ('internal',
            'transit') and move.location_dest_id.usage == 'internal' or
            company_from != company_to):
            ctx = context.copy()
            ctx['force_company'] = company_to.id
            journal_id, acc_src, acc_dest, acc_valuation = \
                self._get_accounting_data_for_valuation(cr, uid, move,
                context=ctx)
            if location_from and location_from.usage == 'customer':
                # goods returned from customer
                self._create_account_move_line(cr, uid, quants, move,
                    acc_dest, acc_valuation, journal_id, context=ctx)
            else:
                self._create_account_move_line(cr, uid, quants, move, acc_src,
                    acc_valuation, journal_id, context=ctx)

        # Create Journal Entry for products leaving the company
        if company_from and (move.location_id.usage == 'internal' and
            move.location_dest_id.usage not in ('internal', 'transit') or
            company_from != company_to):
            ctx = context.copy()
            ctx['force_company'] = company_from.id
            journal_id, acc_src, acc_dest, acc_valuation = \
                self._get_accounting_data_for_valuation(cr, uid, move,
                context=ctx)
            if location_to and location_to.usage == 'supplier':
                # goods returned to supplier
                self._create_account_move_line(cr, uid, quants, move,
                    acc_valuation, acc_src, journal_id, context=ctx)
            else:
                self._create_account_move_line(cr, uid, quants, move,
                    acc_valuation, acc_dest, journal_id, context=ctx)
