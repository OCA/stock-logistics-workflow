# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Akretion (http://www.akretion.com/)
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

from openerp import pooler, SUPERUSER_ID


def migrate(cr, version):
    if not version:
        return

    pool = pooler.get_pool(cr.dbname)
    pto = pool['product.template']

    pt_ids = pto.search(
        cr, SUPERUSER_ID, ['|', ('active', '=', True), ('active', '=', False)])
    for pt in pto.browse(cr, SUPERUSER_ID, pt_ids):
        single = False
        for pp in pt.product_variant_ids:
            cr.execute(
                'select lot_split_type from product_product where id=%s',
                (pp.id, ))
            res = cr.fetchall()
            if res[0][0] == 'single':
                single = True
                break
        if single:
            pto.write(cr, SUPERUSER_ID, pt.id, {'lot_split_type': 'single'})
