# Copyright 2013 - 2021 Agile Business Group sagl (<https://www.agilebg.com>)
# Copyright 2025 bosd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.depends(
        "picking_id.partner_id",
        "product_id",
        "product_id.customer_ids.product_code",
        "product_id.customer_ids.product_name",
        "location_id.warehouse_id.partner_id",
        "location_dest_id.warehouse_id.partner_id",
    )
    def _compute_product_customer_code(self):
        # Gather all partners involved (picking partner + warehouse owner fallback)
        # and pre-fetch all matching customerinfo records in a single query.
        pick_partners = self.mapped("picking_id.partner_id")
        dest_wh_partners = self.mapped("location_dest_id.warehouse_id.partner_id")
        src_wh_partners = self.mapped("location_id.warehouse_id.partner_id")
        all_partners = pick_partners | dest_wh_partners | src_wh_partners

        # Pre-fetch hierarchy fields to avoid per-partner lazy queries in the loop.
        all_partners.fetch(["parent_id", "commercial_partner_id"])
        partner_allowed_ids = {}
        for partner in all_partners:
            partner_allowed_ids[partner.id] = {
                partner.id,
                partner.parent_id.id,
                partner.commercial_partner_id.id,
            } - {False}

        products = self.mapped("product_id")
        all_partner_ids = (
            list(set().union(*partner_allowed_ids.values()))
            if partner_allowed_ids
            else []
        )
        customerinfos = (
            self.env["product.customerinfo"].search(
                [
                    ("partner_id", "in", all_partner_ids),
                    "|",
                    ("product_id", "in", products.ids),
                    "&",
                    ("product_tmpl_id", "in", products.mapped("product_tmpl_id").ids),
                    ("product_id", "=", False),
                ],
                order="sequence,min_qty,price,id",
            )
            if all_partner_ids and products
            else self.env["product.customerinfo"]
        )

        def _find_customerinfo(product, partner):
            if not partner:
                return False
            allowed_ids = partner_allowed_ids.get(partner.id, set())
            first_template_match = False
            product_id = product.id
            template_id = product.product_tmpl_id.id
            for info in customerinfos:
                if info.partner_id.id not in allowed_ids:
                    continue
                info_product_id = info.product_id.id
                if info_product_id == product_id:
                    return info
                if (
                    not info_product_id
                    and not first_template_match
                    and info.product_tmpl_id.id == template_id
                ):
                    first_template_match = info
            return first_template_match

        for move in self:
            product_customer_code = False
            product_customer_name = False
            if move.product_id:
                product = move.product_id
                partner = move.picking_id.partner_id
                info = _find_customerinfo(product, partner)
                # Consignment fallback: look up the warehouse owner when the
                # picking partner yields no match (e.g. vendor receipt into a
                # consignment warehouse owned by a different partner).
                if not info:
                    wh = (
                        move.location_dest_id.warehouse_id
                        or move.location_id.warehouse_id
                    )
                    wh_partner = wh.partner_id if wh else False
                    info = _find_customerinfo(product, wh_partner)
                if info:
                    product_customer_code = info.product_code
                    product_customer_name = info.product_name
            move.product_customer_code = product_customer_code
            move.product_customer_name = product_customer_name

    product_customer_code = fields.Char(
        compute="_compute_product_customer_code",
    )
    product_customer_name = fields.Char(
        compute="_compute_product_customer_code",
    )
