# -*- coding: utf-8 -*-
# © 2014-2015 NDP Systèmes (<http://www.ndp-systemes.fr>)

from openerp import fields, models


class ProcurementRule(models.Model):

    _inherit = 'procurement.rule'

    auto_move = fields.Boolean(
        "Automatic move",
        help="If this option is selected, the generated move will be "
             "automatically processed as soon as the products are available. "
             "This can be useful for situations with chained moves where we "
             "do not want an operator action."
    )
