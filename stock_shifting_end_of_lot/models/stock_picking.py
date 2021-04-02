# Copyright 2020 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date

from odoo import _, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        res = super().button_validate()
        for rec in self:
            if rec._satisfy_condition_for_end_lot_picking():
                end_lot_data = self._get_end_lot_product_and_qty()
                if not end_lot_data:
                    continue
                vals = rec._prepare_end_lot_picking(end_lot_data)
                end_lot_pick = self.env["stock.picking"].create(vals)
                rec._postprocess_end_lot_picking(end_lot_pick, vals.get("origin"))
        return res

    def _postprocess_end_lot_picking(self, end_lot_pick, origin):
        self.message_post(
            body=_(
                "End of lot picking <a href=# data-oe-model="
                "stock.picking data-oe-id=%d>%s</a> created. "
                "You need validate this picking"
            )
            % (end_lot_pick.id, end_lot_pick.name)
        )
        # plan action to validate end_lot
        note = _(
            _(
                "End of lot picking to validate <a href='#' "
                "data-oe-model='%s' data-oe-id='%d'>%s</a>"
            )
        ) % (self._name, end_lot_pick.id, origin)
        end_lot_pick.activity_schedule(
            act_type_xmlid="mail.mail_activity_data_todo",
            user_id=self.env.user.id,
            note=note,
            date_deadline=date.today(),
        )

    def _prepare_end_lot_picking(self, end_lot_data):
        return {
            "picking_type_id": self.picking_type_id.end_lot_picking_type_id.id,
            "origin": "End of lot from %s" % self.name,
            "location_id": self.location_id.id,
            "location_dest_id": self.picking_type_id.end_lot_location_id.id,
            "move_lines": [
                (
                    0,
                    0,
                    {
                        "product_id": x["prd"].id,
                        "name": x["prd"].name,
                        "product_uom": x["prd"].uom_id.id,
                        "product_uom_qty": x["qty"],
                    },
                )
                for x in end_lot_data
            ],
        }

    def _get_end_lot_product_and_qty(self):
        prd_lot = {
            x.product_id: x.move_line_ids.mapped("lot_id")
            for x in self.move_lines
            # We exclude stock.move with several lots to minimize side effects
            if len(x.move_line_ids.mapped("lot_id")) in (1, False)
        }
        if not prd_lot:
            # There is no data to apply some search, we stop the process
            return None
        domain = [("location_id", "child_of", self.location_id.id)]
        if len(prd_lot) > 1:
            domain.extend(["|"] * (len(prd_lot) - 1))
        for domain_line in [
            ["&", ("product_id", "=", prd.id), ("lot_id", "=", lot.id)]
            for prd, lot in prd_lot.items()
        ]:
            domain.extend(domain_line)
        # domain output example:
        # [('location_id', 'child_of', 13),
        #  '|', '|',
        #  '&', ('product_id', '=', 18), ('lot_id', '=', 3),
        #  '&', ('product_id', '=', 35), ('lot_id', '=', 2)]
        #  '&', ('product_id', '=', 42), ('lot_id', '=', 4)]
        return [
            {"prd": x.product_id, "qty": x.quantity - x.reserved_quantity}
            for x in self.env["stock.quant"].search(domain)
            if x.quantity - x.reserved_quantity > 0
        ]

    def _satisfy_condition_for_end_lot_picking(self):
        """Overide this method to define your own cases"""
        if (
            self.picking_type_id.end_lot_location_id
            and self.picking_type_id.end_lot_picking_type_id
        ):
            if (
                self.picking_type_id.end_lot_partner_ids
                and self.partner_id not in self.picking_type_id.end_lot_partner_ids
            ):
                # If partner is not in the specified ones, we skip the behavior
                return False
            # match with any partners
            return True
        return False
