# -*- coding: utf-8 -*-
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
    
stock_move()
