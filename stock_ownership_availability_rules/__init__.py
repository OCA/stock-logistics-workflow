# -*- coding: utf-8 -*-
from . import model

from openerp.api import Environment
from openerp import SUPERUSER_ID


def fill_quant_owner(cr):
    env = Environment(cr, SUPERUSER_ID, {})
    Company = env['res.company']
    orphan_quants = env['stock.quant'].search([('owner_id', '=', False)])

    for quant in orphan_quants:
        quant.owner_id = (
            quant.location_id.partner_id or
            quant.location_id.company_id.partner_id or
            Company.browse(
                Company._company_default_get('stock.quant')
            ).partner_id
        )
