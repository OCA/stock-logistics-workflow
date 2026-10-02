# Copyright 2026 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_procurement_values(self):
        restrict_partner = self.restrict_partner_id
        values = super()._prepare_procurement_values()
        if restrict_partner and self.picking_type_id.code in ["outgoing", "internal"]:
            # purchase_stock clears restrict_partner_id in its override
            self.restrict_partner_id = restrict_partner
            values["restrict_partner_id"] = restrict_partner.id
        return values

    def _search_picking_for_assignation_domain(self):
        domain = super()._search_picking_for_assignation_domain()
        domain += [("owner_id", "=", self.restrict_partner_id.id)]
        return domain

    def _key_assign_picking(self):
        keys = super()._key_assign_picking()
        keys += (self.restrict_partner_id,)
        return keys

    def _get_new_picking_values(self):
        values = super()._get_new_picking_values()
        values["owner_id"] = self.restrict_partner_id.id
        return values
