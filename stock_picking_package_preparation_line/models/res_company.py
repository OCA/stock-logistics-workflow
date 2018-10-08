# Copyright 2015 Francesco Apruzzese - Apulia Software srl
# Copyright 2015-2018 Lorenzo Battistini - Agile Business Group
# Copyright 2016 Alessio Gerace - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ResCompany(models.Model):

    _inherit = 'res.company'

    default_picking_type_for_package_preparation_id = fields.Many2one(
        'stock.picking.type',
        string='Default Picking Type used in package preparation')
