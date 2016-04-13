# -*- coding: utf-8 -*-
# © 2012-2014 Alexandre Fayolle, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import orm, fields


class res_company(orm.Model):
    _name = 'res.company'
    _inherit = 'res.company'
    _columns = {
        'default_picker_id': fields.many2one(
            'res.users', 'Default Picker',
            help='the user to which the pickings are assigned by default',
            select=True),
    }
