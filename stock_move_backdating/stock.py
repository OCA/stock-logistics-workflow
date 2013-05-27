# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 BREMSKERL-REIBBELAGWERKE EMMERLING GmbH & Co. KG
#    Author Marco Dieckhoff
#    Copyright (C) 2013 Agile Business Group sagl (<http://www.agilebg.com>)
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

from osv import fields, osv
from datetime import datetime
from tools.translate import _

class stock_move(osv.osv):
    _name = "stock.move"
    _inherit = _name
        
    _columns = {
         'date_backdating' : fields.datetime("Actual Movement Date", readonly=False, states={'done': [('readonly', True)],'cancel': [('readonly', True)]},
                                            help="Date when the move action was committed. Will set the move date to this date instead of current date when processing to done."),
    }

    def action_done(self, cr, uid, ids, context=None):
        # look at previous state and find date_backdating
        backdating_dates = {}     
        
        for m in self.browse(cr, uid, ids, context=context):
            # if not already in done and date is givven 
            if (m.state != 'done') and (m.date_backdating):
                backdating_dates[m.id] = m.date_backdating
                
        # do actual processing
        result = super(stock_move, self).action_done(cr, uid, ids, context)

        # overwrite date field where applicable        
        for m in self.browse(cr, uid, backdating_dates.keys(), context=context):
            self.write(cr, uid, [m.id], {'date': backdating_dates[m.id]}, context=context)
        
        return result

    
    def on_change_date_backdating(self, cr, uid, ids, date_backdating, context=None):
        """ Test if date is in the past
        @param date_backdating: date
        """
        
        # do nothing if empty
        if (not date_backdating):
            return {}
        
        dt = datetime.strptime(date_backdating, '%Y-%m-%d %H:%M:%S')
        NOW = datetime.now()
        
        if (dt > NOW):
            warning = {'title': _('Error!'),
                   'message':_('You can not process an actual movement date in the future.')}
            values = {'date_backdating': NOW.strftime('%Y-%m-%d %H:%M:%S')}
            return {'warning': warning, 'value': values}

        # otherwise, ok
        return {}
    
    def _create_account_move_line(self, cr, uid, move, src_account_id,
        dest_account_id, reference_amount, reference_currency_id, context=None):
        res=super(stock_move,self)._create_account_move_line(cr, uid, move,
            src_account_id, dest_account_id, reference_amount,
            reference_currency_id, context=context)
        for o2m_tuple in res:
            o2m_tuple[2]['date'] = move.date[:10]
        return res
