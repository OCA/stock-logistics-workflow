# -*- coding: utf-8 -*-

import time
import logging
from openerp.osv import fields, orm
import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DT_FORMAT

_logger = logging.getLogger(__name__)


class transport_plan(orm.Model):
    _name = "transport.plan"
    _description = "Transport Plan"

    _columns = {
        'name': fields.char(
            'Reference',
            required=True,
            readonly=True,
        ),
        'date_eta': fields.date(
            'ETA',
            required=True,
            help="Estimated Date of Arrival"
        ),
        'date_etd': fields.date(
            'ETD',
            help="Estimated Date of Departure"
        ),
        'user_id': fields.many2one(
            'res.users', 'Responsible', required=True,
        ),
        'from_address_id': fields.many2one(
            'res.partner', 'From Address',
            required=True
        ),
        'to_address_id': fields.many2one(
            'res.partner', 'To Address',
            required=True
        ),
        'transport_estimated_cost': fields.float(
            'Transportation Estimated Costs',
            digits_compute=dp.get_precision('Account'),
        ),
        'po_reference': fields.char('PO / RFQ / Tender Reference'),
        'transport_mode_id': fields.many2one(
            'transport.mode',
            string='Transport by',
        ),
        'note': fields.text('Remarks/Description'),
        'state': fields.selection(
            [('draft', 'New'),
             ('in_procurement', 'In Procurement'),
             ('confirmed', 'Confirmed'),
             ('in_transit', 'In Transit'),
             ('customs', 'Customs'),
             ('blocked', 'Blocked'),
             ('done', 'Done'),
             ('cancel', 'Cancel')
             ],
            string='State',
            required=True
        ),
    }

    _defaults = {
        'state': 'draft',
        'user_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).id,
        'name': '/',
    }

    _sql_constraints = [
        ('name_uniq',
         'unique(name)',
         'Transport Plan Reference must be unique'),
    ]

    def create(self, cr, uid, vals, context=None):
        if vals.get('name', '/') == '/':
            seq_obj = self.pool.get('ir.sequence')
            vals['name'] = seq_obj.get(cr, uid, 'transport.plan') or '/'
        return super(transport_plan, self).create(cr, uid, vals,
                                                   context=context)

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update({
            'state': 'draft',
            'name': '/',
        })
        return super(transport_plan, self).copy(cr, uid, id,
                                                default=default,
                                                context=context)

    def set_to_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        return True

    def transport_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
        return True

    def transport_procure(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'in_procurement'}, context=context)
        return True

    def transport_confirm(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'confirmed'}, context=context)
        return True

    def transport_transit(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'in_transit'}, context=context)
        return True

    def transport_at_customs(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'customs'}, context=context)
        return True

    def transport_blocked(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'blocked'}, context=context)
        return True

    def transport_done(self, cr, uid, ids, context=None):
        now = time.strftime(DT_FORMAT)
        self.write(cr, uid, ids,
                   {'state': 'done', 'date_end': now},
                   context=context)
        return True
