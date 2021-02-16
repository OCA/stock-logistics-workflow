# Copyright 2021 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from collections import OrderedDict

from odoo import api, models
from odoo.tools import float_is_zero, float_round


class DeliverySlipReport(models.AbstractModel):
    _name = "report.stock.report_deliveryslip"
    _description = "Delivery Slip Report"

    @api.model
    def _get_remaining_to_deliver(self, picking):
        """Return dictionaries encoding pending quantities to deliver

        Returns a list of dictionaries per sales order, encoding the data
        to be displayed at the end of the delivery slip, summarising for
        each order the pending quantities for each of its lines.
        """
        stock_move = self.env["stock.move"]

        sales_data = OrderedDict()
        for sale in picking.group_id.sale_ids.sorted(key=lambda s: s.id):
            order_name = sale.get_name_for_delivery_line()
            for line in sale.order_line.filtered(
                lambda l: not l.display_type and l.product_id.type != "service"
            ):
                move = stock_move.search(
                    [("sale_line_id", "=", line.id), ("picking_id", "=", picking.id)],
                    limit=1,
                )
                qty = 0
                if picking.state == "done" or not move:
                    # If the picking is done, or if the line is not in any move
                    # of this picking, we rely only in the sales order.
                    qty = line.product_uom_qty - line.qty_delivered
                elif picking.state not in ("cancel", "done"):
                    # Else, we consider the amount reserved in the move.
                    qty = (
                        line.product_uom_qty - line.qty_delivered - move.product_uom_qty
                    )

                uom = move.product_uom if move else line.product_uom
                uom_rounding = uom.rounding
                if not float_is_zero(qty, precision_rounding=uom_rounding):
                    if order_name not in sales_data:
                        sales_data[order_name] = [
                            {"is_header": True, "concept": order_name}
                        ]
                    sales_data[order_name].append(
                        {
                            "is_header": False,
                            "concept": line.product_id.name_get()[0][-1],
                            "qty": float_round(qty, precision_rounding=uom_rounding),
                            "product": line.product_id,
                            "uom": uom,
                            "sale_order_line": line,
                        }
                    )

        return sales_data

    @api.model
    def get_remaining_to_deliver(self, picking):
        sales_data = self._get_remaining_to_deliver(picking)

        # Check: being sales_data an *ordered* dictonary, maybe .values()
        #        returns the items in orders, so would be as easy as:
        #        `return sales_data.values()`
        remaining_to_deliver = []
        for _, sale_data in sales_data.items():
            # Remove those orders having just the line of the title.
            if len(sale_data) > 1:
                remaining_to_deliver.extend(sale_data)
        return remaining_to_deliver

    @api.model
    def rounding_to_precision(self, rounding):
        """ Convert rounding specification to precision digits

        Rounding is encoded in Odoo as a floating number with as
        many meaningful decimals as used for the rounding, e.g.
        0.001 means rounding to 3 decimals. Precision is an integer
        that indicates that amount, directly, in this case 3. This
        method allows to convert from rounding to precision.
        """
        return len(str(int(1 / rounding))) - 1

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env["stock.picking"].browse(docids)
        data = data if data is not None else {}
        docargs = {
            "doc_ids": docids,
            "doc_model": "stock.picking",
            "docs": docs,
            "get_remaining_to_deliver": self.get_remaining_to_deliver,
            "rounding_to_precision": self.rounding_to_precision,
            "data": data.get("form", False),
        }
        return docargs
