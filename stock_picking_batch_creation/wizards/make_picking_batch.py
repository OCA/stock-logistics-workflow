# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import math
from collections import defaultdict

from odoo import api, fields, models, tools

from ..exceptions import NoPickingCandidateError, NoSuitableDeviceError


class MakePickingBatch(models.TransientModel):

    _name = "make.picking.batch"

    picking_type_ids = fields.Many2many(
        comodel_name="stock.picking.type",
        relation="make_picking_batch_picking_type_rel",
        column1="batch_id",
        column2="picking_type_id",
        string="Default operation types",
        help="Default list of eligible operation types when creating a batch transfer",
    )
    stock_device_type_ids = fields.Many2many(
        comodel_name="stock.device.type",
        relation="make_picking_batch_device_type_rel",
        column1="batch_id",
        column2="device_type_id",
        string="Default device types",
        help="Default list of eligible device types when creating a batch transfer",
    )
    user_id = fields.Many2one("res.users", string="Responsible")
    maximum_number_of_preparation_lines = fields.Integer(
        default=20,
        string="Maximum number of preparation lines for the batch",
        required=True,
    )
    group_pickings_by_partner = fields.Boolean(
        default=False,
        string="Group pickings by partner",
        help="All the pickings related to one partner will be put in one bin",
    )

    @api.multi
    def create_batch(self):
        self.ensure_one()
        batch = self._create_batch(raise_if_not_possible=True)
        action = {
            "type": "ir.actions.act_window",
            "name": batch.name,
            "res_model": "stock.picking.wave",
            "res_id": batch.id,
            "view_mode": "form",
            "target": "current",
        }
        return action

    def _search_pickings(self, user=None):
        domain = self._search_pickings_domain(user=user)
        pickings = self.env["stock.picking"].search(domain)
        return pickings

    def _search_pickings_domain(self, user=None):
        domain = [
            ("picking_type_id", "in", self.picking_type_ids.ids),
            ("state", "in", ("partially_available", "assigned")),
            ("wave_id", "=", False),
            ("user_id", "=", user.id if user else False),
        ]
        if not user:
            domain.append(("printed", "=", False))
        return domain

    def _candidates_pickings_to_batch(self, user=None):
        candidates_pickings = self._search_pickings(user=user)
        if not candidates_pickings:
            candidates_pickings = self._search_pickings()
        candidates_pickings.sorted(lambda pick: pick.partner_id.id)
        return candidates_pickings

    def _compute_device_to_use(self, picking):
        available_devices = self.stock_device_type_ids.sorted(lambda d: d.sequence)
        # disable prefetch to ensure we compute weight and volume only
        # for one picking at a time
        picking = picking.with_prefetch()
        picking._init_dimension_fields()

        for device in available_devices:
            if (
                self._volume_condition_for_device_choice(
                    device.min_volume,
                    picking.total_volume_batch_picking,
                    device.max_volume,
                )
                and tools.float_compare(
                    device.max_weight,
                    picking.total_weight_batch_picking,
                    precision_digits=self._precision_volume(),
                )
                > 0
            ):
                return device
        return None

    def _volume_condition_for_device_choice(
        self, min_volume, picking_volume, max_volume
    ):
        lower_bound = tools.float_compare(picking_volume, min_volume, 2) >= 0
        upper_bound = tools.float_compare(max_volume, picking_volume, 2) >= 0
        return lower_bound and upper_bound

    def _get_first_suitable_device_and_picks(self, pickings):
        """Get the first suitable device and the list of pickings where all the
        pickings before the first one providing a suitable device are removed
        """
        selected_device = None
        suitable_pick_ids = []
        for pick in pickings:
            if not self._lock_selected_picking(pick):
                continue
            device = self._compute_device_to_use(pick)
            if device and not selected_device:
                selected_device = device
            if device and device == selected_device:
                suitable_pick_ids.append(pick.id)

        if selected_device:
            return (
                selected_device,
                self.env["stock.picking"].browse(suitable_pick_ids),
            )
        return (
            self.env["stock.device.type"].browse(),
            self.env["stock.picking"].browse(),
        )

    def _create_batch(self, raise_if_not_possible=False):
        user = self.user_id if self.user_id else self.env.user
        candidates_pickings_to_batch = self._candidates_pickings_to_batch(user=user)
        if not candidates_pickings_to_batch:
            if raise_if_not_possible:
                raise NoPickingCandidateError()
            return self.env["stock.picking.wave"].browse()

        (
            device,
            candidates_pickings_to_batch,
        ) = self._get_first_suitable_device_and_picks(candidates_pickings_to_batch)

        if not device:
            if raise_if_not_possible:
                raise NoSuitableDeviceError(candidates_pickings_to_batch)
            return self.env["stock.picking.wave"].browse()

        (selected_pickings, unselected_pickings, used_nbr_bins) = self._apply_limits(
            candidates_pickings_to_batch, device
        )
        if not selected_pickings:
            selected_pickings = unselected_pickings[:1]
        if not selected_pickings:
            if raise_if_not_possible:
                raise NoPickingCandidateError()
            return self.env["stock.picking.wave"].browse()
        vals = self._create_batch_values(user, device, selected_pickings)
        batch = self.env["stock.picking.wave"].create(vals)
        batch._init_wave_info(used_nbr_bins)
        return batch

    def _precision_weight(self):
        return self.env["decimal.precision"].precision_get("Product Unit of Measure")

    def _precision_volume(self):
        return max(
            6,
            self.env["decimal.precision"].precision_get("Product Unit of Measure") * 2,
        )

    def _apply_limits(self, pickings, device, max_pickings=0):
        """
        Once we have the candidates pickings for clustering,
        we need to decide when to stop the cluster (i.e.,
        when to stop adding pickings in it)
        We add pickings in the cluster as long as the conditions are respected
        """
        selected_picking_ids = []
        total_weight = 0.0
        total_volume = 0.0
        total_nbr_picking_lines = 0
        precision_weight = self._precision_weight()
        precision_volume = self._precision_volume()

        def gt(value1, value2, digits):
            """Return True if value1 is greater than value2"""
            return tools.float_compare(value1, value2, precision_digits=digits) == 1

        # # Add pickings to the first one as long as
        # # - total volume is not outreached
        # # - total weight is not outreached
        # # - maximum number of preparation lines is not outreached
        # # - numbers of bins available is greater than 0
        # # - The device for the current picking is supposed to be
        available_nbr_bins = device.nbr_bins
        volume_by_partners = defaultdict(lambda: 0)
        for picking in pickings:
            if not self._lock_selected_picking(picking):
                continue
            if available_nbr_bins == 0:
                break

            if max_pickings and len(selected_picking_ids) == max_pickings:
                # selected enough!
                break

            # Check that the picking can go on the selected device
            picking_device = self._compute_device_to_use(picking)
            if device != picking_device:
                continue
            picking._init_nbr_bins_on_device_field(device)

            nbr_bins = picking.nbr_bins_batch_picking
            old_volume = volume_by_partners[picking.partner_id]
            new_volume = old_volume + picking.total_volume_batch_picking
            if self.group_pickings_by_partner:
                nbr_bins = math.ceil(new_volume / device.volume_per_bin) - math.ceil(
                    old_volume / device.volume_per_bin
                )

            available_bins_outreached = available_nbr_bins - nbr_bins < 0
            if available_bins_outreached:
                continue

            weight_limit_outreached = device.max_weight and gt(
                total_weight + picking.total_weight_batch_picking,
                device.max_weight,
                precision_weight,
            )
            if weight_limit_outreached:
                continue

            volume_limit_outreached = device.max_volume and gt(
                total_volume + picking.total_volume_batch_picking,
                device.max_volume,
                precision_volume,
            )
            if volume_limit_outreached:
                continue

            nbr_lines_limit_outreached = (
                self.maximum_number_of_preparation_lines
                and gt(
                    total_nbr_picking_lines + picking.nbr_picking_lines,
                    self.maximum_number_of_preparation_lines,
                    1,
                )
            )
            if nbr_lines_limit_outreached:
                continue

            # All conditions are OK : we keep the picking in the cluster
            selected_picking_ids.append(picking.id)
            total_weight += picking.total_weight_batch_picking
            total_volume += picking.total_volume_batch_picking
            total_nbr_picking_lines += picking.nbr_picking_lines
            available_nbr_bins -= nbr_bins
            volume_by_partners[picking.partner_id] = new_volume

        selected_pickings = self.env["stock.picking"].browse(selected_picking_ids)
        unselected_pickings = pickings - selected_pickings
        used_nbr_bins = device.nbr_bins - available_nbr_bins
        return selected_pickings, unselected_pickings, used_nbr_bins

    def _lock_selected_picking(self, picking):
        """ Method hook called to lock the selected picking and ensure that
        nothing has changed in the timelapse between the search request and
        the addition to the batch that will prevent a normal commit of the
        transaction. If nothing is returned by the method, the selected picking
        will not be added to the batch.
        Implementation example:
        .. code-block:: python
             self.env.cr.execute('''
                SELECT
                    id
                FROM
                    stock_picking
                WHERE
                    id = %s
                FOR UPDATE OF stock_picking SKIP LOCKED;
            ''', (picking.id, ))
            _id = [r[0] for r in self.env.cr.fetchall()]
            if _id:
                return self.env["stock.picking"].browse(_id)
            return None
        """
        return picking

    def _create_batch_values(self, user, device, pickings):
        return {
            "picking_ids": [(6, 0, pickings.ids)],
            "user_id": user.id,
            "state": "draft",
            "picking_device_id": device.id if device else None,
        }
