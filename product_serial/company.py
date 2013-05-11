# -*- encoding: utf-8 -*-
##############################################################################
#
#    Product serial module for OpenERP
#    Copyright (C) 2010-2011 Anevia. All Rights Reserved
#    Copyright (C) 2013 Akretion
#    @author: Sebastien Beau <sebastien.beau@akretion.com>
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
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

from osv import osv, fields

class company(osv.osv):
    _inherit = 'res.company'

    _columns = {
        'autosplit_is_active': fields.boolean('Active auto split', help="Active the automatic split of move lines on the pickings."),
        'is_group_invoice_line': fields.boolean('Group invoice lines', help="If active, OpenERP will group the identical invoice lines. If inactive, each move line will generate one invoice line."),
    }

    _defaults = {
        'autosplit_is_active': True,
        'is_group_invoice_line': True,
    }


