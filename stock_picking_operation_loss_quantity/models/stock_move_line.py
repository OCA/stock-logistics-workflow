# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2018 Okia SPRL <sylvain@okia.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import defaultdict, namedtuple

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Command, float_compare, float_round

MoveLineGroupKey = namedtuple(
    "MoveLineGroupKey",
    ["location_id", "product_id", "package_id", "lot_id", "owner_id"],
)


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    is_action_loss_qty_allowed = fields.Boolean(
        compute="_compute_is_action_loss_qty_allowed"
    )

    @api.depends("reserved_qty", "qty_done", "picking_id.picking_type_code")
    def _compute_is_action_loss_qty_allowed(self):
        for rec in self:
            rec.is_action_loss_qty_allowed = (
                rec.location_id.warehouse_id.use_loss_picking
                and (rec.qty_done - rec.reserved_qty < 0)
                and rec.state not in ("done", "draft")
                and rec.picking_id.picking_type_code != "incoming"
            )

    def _check_is_action_loss_qty_allowed(self):
        if any(not rec.is_action_loss_qty_allowed for rec in self):
            raise UserError(_("You are not allowed to declare loss quantities"))

    def action_loss_quantity(self):
        """This action process the operation and makes the remaining qty no more
        available into the stock at the same time of creating a picking to
        search for the qty loss. At the end, we try to recompute a new move line
        to find qty into an other place to complete the move.
        """
        self._check_is_action_loss_qty_allowed()
        wizard = self.env["stock.picking.operation.loss.quantity"].create(
            {
                "move_line_ids": [Command.set(self.ids)],
            }
        )
        return wizard.action_lose_quantity()

    def _group_move_lines_for_loss(self):
        """
        Return a list of move lines by MoveLineGroupKey
        """
        ret = defaultdict(list)
        for rec in self:
            key = MoveLineGroupKey(
                location_id=rec.location_id,
                product_id=rec.product_id,
                package_id=rec.package_id,
                lot_id=rec.lot_id,
                owner_id=rec.owner_id,
            )
            ret[key].append(rec.id)

        return {k: self.browse(v) for k, v in ret.items()}

    def _prepare_values_for_loss_movement(self, group_key):
        """
            Careful: Lines are here for reference only as values are grouped in
                     group key

        :param group_key: _description_
        :type group_key: _type_
        :param quantity: _description_
        :type quantity: _type_
        :return: _description_
        :rtype: _type_
        """
        self.ensure_one()
        pick_type_id = group_key.location_id.warehouse_id.loss_type_id

        quants_quantity = self.env["stock.quant"]._get_available_quantity(
            group_key.product_id,
            group_key.location_id,
            lot_id=group_key.lot_id,
            package_id=group_key.package_id,
            owner_id=group_key.owner_id,
        )
        loss_quantity = float_round(
            quants_quantity - self.qty_done,
            precision_rounding=self.product_uom_id.rounding,
            rounding_method="HALF-UP",
        )

        self.env["stock.quant"]._update_reserved_quantity(
            group_key.product_id,
            group_key.location_id,
            loss_quantity,
            group_key.lot_id,
            group_key.package_id,
            group_key.owner_id,
        )
        move_line = {
            "reserved_uom_qty": loss_quantity,
            "product_id": group_key.product_id.id,
            "picking_type_id": pick_type_id.id,
            "location_id": group_key.location_id.id,
            "location_dest_id": pick_type_id.default_location_dest_id.id,
            "lot_id": group_key.lot_id.id,
            "origin": "Operator: %s / Pickings: %s"
            % (
                self.env.user.name,
                ", ".join(self.mapped("picking_id.name")),
            ),
        }
        return move_line

    def _create_loss_picking(self, group_key):
        loss_line_values = []
        for line in self:
            # Free the reserved quantity with the done one in order to be able to reserve
            # the quant for the loss movement
            line.reserved_uom_qty = line.qty_done
            loss_line_values.append(
                Command.create(line._prepare_values_for_loss_movement(group_key))
            )
        if not loss_line_values:
            raise ValidationError(
                _("You try to create a Loss picking without any loss movement!")
            )
        pick_type_id = group_key.location_id.warehouse_id.loss_type_id
        if not pick_type_id:
            raise ValidationError(
                _(
                    "You don't have a Loss picking type enabled on your Warehouse! "
                    "Please check the 'Enable the Loss feature' in your warehouse "
                    "configuration."
                )
            )
        if not pick_type_id.default_location_dest_id:
            raise ValidationError(
                _(
                    "You don't have any default destination set on your Loss picking type!"
                )
            )
        loss_picking = self.env["stock.picking"].create(
            {
                "picking_type_id": pick_type_id.id,
                "location_id": group_key.location_id.id,
                "location_dest_id": pick_type_id.default_location_dest_id.id,
                "move_line_ids": loss_line_values,
            }
        )
        return loss_picking

    def _get_saved_operations_for_loss(self, group_key, operations_by_move):
        """
            Save already begun stock operations
        :param operations_by_move: _description_
        :type operations_by_move: defaultdict(dict)
        """
        for line in self:
            if line.qty_done:
                # In order to not lose any information, copy the recordset to
                # a memory one
                values = line._convert_to_write(line._cache).copy()
                operations_by_move[group_key][line.id] = values

    def _split_for_loss(self) -> dict:
        """
        This method imitates the _put_in_pack() method as it
        copies the existing line into a new one and set
        """
        splitted_lines_result = dict()
        for line in self:
            done_to_keep = line.qty_done
            if (
                float_compare(
                    done_to_keep, 0, precision_rounding=line.product_uom_id.rounding
                )
                <= 0
            ):
                continue
            # quantity_left_todo = float_round(
            #     line.reserved_uom_qty - done_to_keep,
            #     precision_rounding=line.product_uom_id.rounding,
            #     rounding_method="HALF-UP",
            # )
            new_move_line = line.copy(
                default={"reserved_uom_qty": 0, "qty_done": line.qty_done}
            )
            vals = {"reserved_uom_qty": 0.0, "qty_done": 0.0}
            line.write(vals)
            new_move_line.write({"reserved_uom_qty": done_to_keep})
            splitted_lines_result[line] = new_move_line
        return splitted_lines_result
