# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from openerp import models, api


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.model
    def _run_move_create(self, procurement):
        res = super(ProcurementOrder, self)._run_move_create(procurement)
        if procurement.sale_line_id.sequence:
            res.update({'sequence': procurement.sale_line_id.sequence})
        return res
