# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import api, fields, models
from odoo.tools import float_compare


class StockPicking(models.Model):

    _inherit = "stock.picking"

    assignation_max_weight = fields.Float(
        compute="_compute_assignation_max_weight",
        digits="Stock Weight",
        store=True,
        help="Technical field that represent the maximum weight for a move that"
        "is acceptable for this picking assignation",
        states={"done": [("readonly", True)], "cancel": [("readonly", True)]},
    )

    @property
    def _assignation_max_weight_precision(self):
        return self._fields["assignation_max_weight"].get_digits(self.env)[1]

    @api.depends("picking_type_id", "weight", "state")
    def _compute_assignation_max_weight(self):
        precision_digits = self._assignation_max_weight_precision
        for picking in self.filtered(
            lambda picking: picking.state not in ("draft", "done", "cancel")
        ):
            max_weight = (
                picking.picking_type_id.group_pickings_maxweight - picking.weight
            )
            if (
                float_compare(
                    max_weight,
                    picking.assignation_max_weight,
                    precision_digits=precision_digits,
                )
                != 0
            ):
                # only update if the value has changed
                picking.assignation_max_weight = max_weight

    @api.model
    def _get_index_for_grouping_fields(self):
        """
        This tuple is intended to be overriden in order to add fields
        used in groupings
        """
        res = super()._get_index_for_grouping_fields()
        if "assignation_max_weight" not in res:
            res.append("assignation_max_weight")
        return res

    def init(self):
        """
        This has to be called in every overriding module
        """
        self._create_index_for_grouping()

    def _should_be_split_for_max_weight(self):
        """
        Return True if the picking should be split
        """
        self.ensure_one()
        return (
            self.state not in ["done", "cancel"]
            and not self.printed
            and self.picking_type_id.group_pickings_maxweight
            and float_compare(
                self.weight,
                self.picking_type_id.group_pickings_maxweight,
                precision_digits=self._assignation_max_weight_precision,
            )
            > 0
        )

    def _split_for_max_weight(self):
        """
        Split the picking in several pickings if the total weight is
        greater than the max weight of the picking type
        """
        precision_digits = self._assignation_max_weight_precision
        for picking in self:
            if not picking._should_be_split_for_max_weight():
                continue
            # we create batch of move's ids to reassign. To do so, we
            # iterate over the move lines and we add the move to the current
            # batch while the total weight of the batch is less than the max
            # weight of the picking type. When the total weight of the batch
            # is exceeded, we create a new batch of ids to reassign.
            ids_to_reassign_by_batch = defaultdict(list)
            batch_id = 0
            total_weight = 0
            # we must ignore the first batch of ids to reassign because it
            # will be the current picking
            max_weight = picking.picking_type_id.group_pickings_maxweight
            for move in picking.move_ids:
                total_weight += move.weight
                if (
                    float_compare(
                        total_weight,
                        max_weight,
                        precision_digits=precision_digits,
                    )
                    > 0
                ):
                    batch_id += 1
                    total_weight = move.weight
                ids_to_reassign_by_batch[batch_id].append(move.id)
            # we create the new pickings for each batch except the first one
            # which is the current picking
            first = True
            for ids_to_reassign in ids_to_reassign_by_batch.values():
                if first:
                    first = False
                    continue
                moves = self.env["stock.move"].browse(ids_to_reassign)
                moves._assign_picking()
