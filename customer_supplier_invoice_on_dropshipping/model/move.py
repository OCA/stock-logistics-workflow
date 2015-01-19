#    Author: Leonardo Pistone
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
from openerp import models, api


class Move(models.Model):
    _inherit = "stock.move"

    @api.model
    def _get_master_data(self, move, company):
        partner, uid, currency = super(Move, self)._get_master_data(move,
                                                                    company)
        new_partner_id = self.env.context.get('partner_to_invoice_id')
        if new_partner_id:
            partner = self.env['res.partner'].browse(new_partner_id)
        return partner, uid, currency
