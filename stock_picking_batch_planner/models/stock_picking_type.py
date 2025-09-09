# Copyright 2025 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, exceptions, fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    plan_batch = fields.Boolean(
        string="Planned Batches",
        help="Place Stock Operations in Batches or Waves when planned from the "
        "Batch of the destiny moves.\n"
        "Uses same criteria as Auto-Batches to decide how to "
        "plan batches/waves.",
    )
    # Those fields are used to allow Odoo use Auto-Batch logic when planning batches
    # without changing the behavior of Auto-Batch feature.
    auto_batch = fields.Boolean(
        compute="_compute_auto_batch",
        inverse="_inverse_auto_batch",
        store=False,
        readonly=False,
    )
    auto_batch_original = fields.Boolean(
        string="Automatic Batches (original value)",
        help="Field used to store the original value of `auto_batch` field.",
    )

    @api.depends_context("plan_batch")
    @api.depends("auto_batch_original")
    def _compute_auto_batch(self):
        """Return True if `plan_batch` is True in context,
        otherwise return the original value"""
        plan_batch = bool(self.env.context.get("plan_batch", False))
        for record in self:
            record.auto_batch = plan_batch or record.auto_batch_original

    def _inverse_auto_batch(self):
        """Store the original value of `auto_batch` in `auto_batch_original`.
        If `auto_batch` is set to True, also set `plan_batch` to True."""
        for record in self:
            record.auto_batch_original = record.auto_batch
            if record.auto_batch_original:
                record.plan_batch = record.auto_batch_original

    @api.model
    def _get_view(self, view_id=None, view_type="form", **options):
        """Change invisible criteria to show items when `plan_batch` or
        `auto_batch` fields are set.
        This is needed because Odoo uses `auto_batch` field to show/hide some
        fields in the form view and other modules can add this type of groups.
        This way we ensure that those fields are also hidden/shown properly."""
        arch, view = super()._get_view(view_id, view_type, **options)
        if view_type == "form":
            for node in arch.xpath("//*"):
                if (
                    node.attrib.get("invisible", False)
                    and "not auto_batch" in node.attrib["invisible"]
                ):
                    node.set(
                        "invisible",
                        f"not plan_batch and ({node.attrib['invisible']})",
                    )
        return arch, view

    @api.model
    def _is_auto_batch_grouped(self):
        """Check if picking type allow perform batches if comes from batch planning"""
        self.ensure_one()
        # Check first if comes from batch planning
        if (
            self.env.context.get("plan_batch")
            and self.plan_batch
            and any(self[key] for key in self._get_batch_group_by_keys())
        ):
            return True
        return super()._is_auto_batch_grouped()

    @api.model
    def _is_auto_wave_grouped(self):
        """Check if picking type allow perform waves if comes from batch planning"""
        self.ensure_one()
        # Check first if comes from batch planning
        if (
            self.env.context.get("plan_batch")
            and self.plan_batch
            and any(self[key] for key in self._get_wave_group_by_keys())
        ):
            return True
        return super()._is_auto_wave_grouped()

    @api.constrains(
        lambda self: self._get_batch_and_wave_group_by_keys() + ["plan_batch"]
    )
    def _validate_plan_batch_group_by(self):
        """Ensure that if `plan_batch` is True,
        at least one group by option is selected"""
        group_by_keys = self._get_batch_and_wave_group_by_keys()
        for picking_type in self:
            if not picking_type.plan_batch:
                continue
            if not any(picking_type[key] for key in group_by_keys):
                raise exceptions.ValidationError(
                    self.env._(
                        "If the Planned Batches feature is enabled, "
                        "at least one 'Group by' option must be selected."
                    )
                )
