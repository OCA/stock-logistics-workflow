# Copyright (C) 2018 Akretion (<http://www.akretion.com>)
# @author: Florian da Costa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _action_confirm(self):
        for order in self:
            order._set_dropship_route_on_adhoc_cases()
        super()._action_confirm()

    def _set_dropship_route_on_adhoc_cases(self):
        """ Assign a dropship route to sale lines which have
            the same vendor than dropship product
        """
        self.ensure_one()
        vendor_dropsh, vendor_line = self._get_dropship_info()
        to_write_sale_lines = self.env["sale.order.line"]
        for vendor, line in vendor_dropsh.items():
            lines_to_dropshipping = vendor_line.get(vendor)
            if lines_to_dropshipping:
                to_write_sale_lines |= lines_to_dropshipping
        to_write_sale_lines.write(
            {"route_id": self.env.ref(
             "stock_dropshipping.route_drop_shipping").id})
        products = []
        for __, val in vendor_line.items():
            for x in val:
                products.append(x.name)
        body = _(
            "Products '%s' are provided by a dropship order" %
            ", ".join(products))
        if products:
            self.message_post(body=body)
        return True

    def _get_dropship_info(self):
        """ 2 info:
            vendor_dropsh: dropship line by vendor
                {partner_obj.id: sale_line_obj}
            vendor_line: product line by vendor among dropship vendors
                {partner_obj.id: sale_line_obj}
        """
        self.ensure_one()
        dropsh_route = self.env.ref(
            "stock_dropshipping.route_drop_shipping")
        line_obj = self.env["sale.order.line"]
        vendor_dropsh = {}
        vendor_line = {}
        for line in self.order_line:
            vendor = line.product_id._select_seller(
                quantity=line.product_uom_qty).name
            if not vendor or not vendor.allow_whole_order_dropshipping:
                continue
            product_route_ids = line.product_id.route_ids.ids + \
                line.product_id.categ_id.route_ids.ids
            if (line.route_id and line.route_id == dropsh_route) or \
                    dropsh_route.id in product_route_ids:
                # a dropship product here
                vendor_dropsh[vendor] = (
                    vendor_dropsh.get(vendor, line_obj) + line)
            else:
                # other products here
                vendor_line[vendor] = (
                    vendor_line.get(vendor, line_obj) + line)
        return (vendor_dropsh, vendor_line)
