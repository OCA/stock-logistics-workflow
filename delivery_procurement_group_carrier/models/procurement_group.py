# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# Copyright 2020-2021 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    carrier_id = fields.Many2one("delivery.carrier", string="Delivery Method")
