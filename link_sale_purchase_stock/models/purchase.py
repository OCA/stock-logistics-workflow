# Copyright 2020 KEMA SK, s.r.o. - Radovan Skolnik <radovan@skolnik.info>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    sale_order_count = fields.Integer(
        "Number of Source Sale",
        compute="_compute_sale_order_count",
        groups="sales_team.group_sale_salesman",
    )

    @api.depends(
        "order_line.sale_order_id", "order_line.move_dest_ids.group_id.sale_id"
    )
    def _compute_sale_order_count(self):
        for purchase in self:
            purchase.sale_order_count = len(purchase._get_sale_orders())

    def _get_sale_orders(self):
        return (
            self.order_line.sale_order_id
            | self.order_line.move_dest_ids.group_id.sale_id
        )

    def action_view_sale_orders(self):
        self.ensure_one()
        sale_order_ids = self._get_sale_orders().ids
        action = {
            "res_model": "sale.order",
            "type": "ir.actions.act_window",
        }
        if len(sale_order_ids) == 1:
            action.update(
                {"view_mode": "form", "res_id": sale_order_ids[0],}
            )
        else:
            action.update(
                {
                    "name": _("Sources Sale Orders %s" % self.name),
                    "domain": [("id", "in", sale_order_ids)],
                    "view_mode": "tree,form",
                }
            )
        return action


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.model
    def _prepare_purchase_order_line(
        self, product_id, product_qty, product_uom, company_id, supplier, po
    ):
        partner = supplier.name
        uom_po_qty = product_uom._compute_quantity(product_qty, product_id.uom_po_id)
        # _select_seller is used if the supplier have different price depending
        # the quantities ordered.
        seller = product_id.with_context(force_company=company_id.id)._select_seller(
            partner_id=partner,
            quantity=uom_po_qty,
            date=po.date_order and po.date_order.date(),
            uom_id=product_id.uom_po_id,
        )

        taxes = product_id.supplier_taxes_id
        fpos = po.fiscal_position_id
        taxes_id = fpos.map_tax(taxes, product_id, seller.name)
        if taxes_id:
            taxes_id = taxes_id.filtered(lambda x: x.company_id.id == company_id.id)

        price_unit = (
            self.env["account.tax"]._fix_tax_included_price_company(
                seller.price, product_id.supplier_taxes_id, taxes_id, company_id
            )
            if seller
            else 0.0
        )
        if (
            price_unit
            and seller
            and po.currency_id
            and seller.currency_id != po.currency_id
        ):
            price_unit = seller.currency_id._convert(
                price_unit,
                po.currency_id,
                po.company_id,
                po.date_order or fields.Date.today(),
            )

        product_lang = product_id.with_context(
            lang=partner.lang, partner_id=partner.id,
        )
        name = product_lang.display_name
        if product_lang.description_purchase:
            name += "\n" + product_lang.description_purchase

        date_planned = self._get_date_planned(seller, po=po)

        return {
            "name": name,
            "product_qty": uom_po_qty,
            "product_id": product_id.id,
            "product_uom": product_id.uom_po_id.id,
            "price_unit": price_unit,
            "date_planned": date_planned,
            "taxes_id": [(6, 0, taxes_id.ids)],
            "order_id": po.id,
        }

    @api.model
    def _prepare_purchase_order_line_from_procurement(
        self, product_id, product_qty, product_uom, company_id, values, po
    ):
        supplier = values.get("supplier")
        res = self._prepare_purchase_order_line(
            product_id, product_qty, product_uom, company_id, supplier, po
        )
        res["move_dest_ids"] = [(4, x.id) for x in values.get("move_dest_ids", [])]
        res["orderpoint_id"] = (
            values.get("orderpoint_id", False) and values.get("orderpoint_id").id
        )
        res["propagate_cancel"] = values.get("propagate_cancel")
        res["propagate_date"] = values.get("propagate_date")
        res["propagate_date_minimum_delta"] = values.get("propagate_date_minimum_delta")
        return res

    def _find_candidate(
        self,
        product_id,
        product_qty,
        product_uom,
        location_id,
        name,
        origin,
        company_id,
        values,
    ):
        """ Return the record in self where the procument with values passed as
        args can be merged. If it returns an empty record then a new line will
        be created.
        """
        lines = self.filtered(
            lambda l: l.propagate_date == values["propagate_date"]
            and l.propagate_date_minimum_delta == values["propagate_date_minimum_delta"]
            and l.propagate_cancel == values["propagate_cancel"]
            and l.orderpoint_id == values["orderpoint_id"]
        )
        return lines and lines[0] or self.env["purchase.order.line"]

    def _prepare_stock_moves(self, picking):
        res = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        res[0]["location_dest_id"] = (
            self.orderpoint_id
            and self.orderpoint_id.location_id.id
            or self.order_id._get_destination_location()
        )
        return res
