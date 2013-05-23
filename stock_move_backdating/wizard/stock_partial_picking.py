# -*- coding: utf-8 -*-
from osv import fields, osv
from datetime import datetime
from tools.translate import _

class stock_partial_picking_line(osv.TransientModel):

    _name = "stock.partial.picking.line"
    _columns = {
    	'date_backdating': fields.related('move_id', 'date_backdating', type="datetime", string="Actual Movement Date")
    }
