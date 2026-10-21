# Copyright (C) 2023-Today:
# Dinamiche Aziendali Srl (<http://www.dinamicheaziendali.it/>)
# @author: Marco Calcagni <mcalcagni@dinamicheaziendali.it>
# @author: Giuseppe Borruso <gborruso@dinamicheaziendali.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import copy

from odoo import models


class Product(models.Model):
    _inherit = "product.product"

    def _get_cost(self):
        # overridable method to customize cost used for evaluation
        self.ensure_one()
        return self.standard_price

    def _compute_qty_available(self, to_date):
        res = self._compute_quantities_available(to_date)
        return res

    def _compute_quantities_available(self, to_date=False):
        date = to_date

        # get quants
        quan = {}
        self.env.cr.execute(
            """
            SELECT
                stock_quant.quantity,
                stock_quant.product_id,
                stock_quant.location_id,
                stock_quant.lot_id,
                stock_quant.package_id,
                stock_quant.owner_id,
                stock_quant.id
            FROM
                stock_quant,
                stock_location
            WHERE
                stock_quant.location_id = stock_location.id
                AND stock_quant.product_id = %s
                AND stock_location.company_id = %s
            ORDER BY
                stock_quant.product_id,
                stock_quant.location_id,
                stock_quant.lot_id,
                stock_quant.package_id,
                stock_quant.owner_id;
        """,
            (self.id, self.env.user.company_id.id),
        )

        for row2 in self._cr.fetchall():
            quant_qty = row2[0] * 1.0
            product_id = row2[1]
            location_id = row2[2]
            lot_id = (
                row2[3] if self.tracking != "serial" and row2[3] is not None else False
            )
            package_id = row2[4] if row2[4] and row2[4] is not None else False
            owner_id = row2[5] if row2[5] and row2[5] is not None else False
            key = "%d_%d_%d_%d_%d" % (
                product_id,
                location_id,
                lot_id,
                package_id,
                owner_id,
            )
            if key in quan.keys():
                quan[key] = quan[key] + quant_qty
            else:
                quan[key] = quant_qty * 1.0

        # rename quan -> move
        move = quan

        # duplicate quan dict
        stock_now = copy.deepcopy(quan)

        # recompute moves if set request date
        # moves +
        self.env.cr.execute(
            """
            SELECT
                SUM(stock_move_line.qty_done),
                stock_move_line.product_id,
                stock_move_line.location_id,
                stock_move_line.lot_id,
                stock_move_line.package_id,
                stock_move_line.owner_id,
                stock_move_line.date
            FROM
                stock_move_line
            WHERE
                stock_move_line.date >= %s
                AND stock_move_line.state = 'done'
                AND stock_move_line.product_id = %s
                AND stock_move_line.company_id = %s
            GROUP BY
                stock_move_line.product_id,
                stock_move_line.location_id,
                stock_move_line.lot_id,
                stock_move_line.package_id,
                stock_move_line.owner_id,
                stock_move_line.date
            ORDER BY
                stock_move_line.product_id,
                stock_move_line.location_id,
                stock_move_line.lot_id,
                stock_move_line.package_id,
                stock_move_line.owner_id,
                stock_move_line.date desc;
        """,
            (date, self.id, self.env.user.company_id.id),
        )

        for row in self._cr.fetchall():
            move_qty = row[0]
            product_id = row[1]
            location_id = row[2]
            lot_id = (
                row[3] if self.tracking != "serial" and row[3] is not None else False
            )
            package_id = row[4] if row[4] and row[4] is not None else False
            owner_id = row[5] if row[5] and row[5] is not None else False
            key = "%d_%d_%d_%d_%d" % (
                product_id,
                location_id,
                lot_id,
                package_id,
                owner_id,
            )
            if key in move.keys():
                move[key] += move_qty
            else:
                move[key] = move_qty
                stock_now[key] = 0

        # moves -
        self.env.cr.execute(
            """
            SELECT
                SUM(stock_move_line.qty_done),
                stock_move_line.product_id,
                stock_move_line.location_dest_id,
                stock_move_line.lot_id,
                stock_move_line.package_id,
                stock_move_line.owner_id,
                stock_move_line.date
            FROM
                stock_move_line
            WHERE
                stock_move_line.date >= %s
                AND stock_move_line.state='done'
                AND stock_move_line.product_id = %s
                AND stock_move_line.company_id = %s
            GROUP BY
                stock_move_line.product_id,
                stock_move_line.location_dest_id,
                stock_move_line.lot_id,
                stock_move_line.package_id,
                stock_move_line.owner_id,
                stock_move_line.date
            ORDER BY
                stock_move_line.product_id,
                stock_move_line.location_dest_id,
                stock_move_line.lot_id,
                stock_move_line.package_id,
                stock_move_line.owner_id,
                stock_move_line.date desc;
        """,
            (date, self.id, self.env.user.company_id.id),
        )

        for row in self._cr.fetchall():
            move_qty = row[0]
            product_id = row[1]
            location_dest_id = row[2]
            lot_id = (
                row[3] if self.tracking != "serial" and row[3] is not None else False
            )
            package_id = row[4] if row[4] and row[4] is not None else False
            owner_id = row[5] if row[5] and row[5] is not None else False
            key = "%d_%d_%d_%d_%d" % (
                product_id,
                location_dest_id,
                lot_id,
                package_id,
                owner_id,
            )
            if key in move.keys():
                move[key] -= move_qty
            else:
                move[key] = -move_qty
                stock_now[key] = 0

        # compute
        list_internal_quant = []
        for key, _qty in move.items():
            key_split = key.split("_")
            product_id = int(key_split[0])
            uom_id = self.env["product.product"].browse(product_id).uom_id.id
            location_id = int(key_split[1])
            lot_id = int(key_split[2])
            if lot_id == 0:
                lot_id = None
            package_id = int(key_split[3])
            if package_id == 0:
                package_id = None
            owner_id = int(key_split[4])
            if owner_id == 0:
                owner_id = None
            mov = move[key] or 0.0
            qua = stock_now[key] or 0.0
            dif = qua - mov

            # only internal locations
            location_obj = self.env["stock.location"].search(
                [("id", "=", location_id)], limit=1
            )
            if location_obj.usage == "internal":
                list_internal_quant.append(
                    {
                        "date": date,
                        "product_id": product_id,
                        "uom_id": uom_id,
                        "location_id": location_id,
                        "lot_id": lot_id,
                        "package_id": package_id,
                        "owner_id": owner_id,
                        "stock_at_date": mov,
                        "stock_now": qua,
                        "diff_qty": dif,
                    }
                )
        return list_internal_quant
