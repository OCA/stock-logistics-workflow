# -*- coding: utf-8 -*-
# © 2012-2014 Alexandre Fayolle, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'
    default_picker_id = fields.Many2one(
        'res.users', 'Default Picker',
        help='the user to which the pickings are assigned by default',
        index=True,
    )
