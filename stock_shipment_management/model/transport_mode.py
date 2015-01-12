# -*- coding: utf-8 -*-

from openerp.osv import fields, orm


class transport_mode(orm.Model):
    _name = "transport.mode"
    _columns = {
        'name': fields.char('Transport Mode', size=32, required=True),
    }
