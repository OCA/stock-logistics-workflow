# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class LeadTimeProfile(models.Model):
    _name = "lead.time.profile"
    _description = "Lead Time Profile"
    _order = "country_id, state_id, partner_id, warehouse_id"

    warehouse_id = fields.Many2one(
        "stock.warehouse", help="Matched against the warehouse of the sales order."
    )
    partner_id = fields.Many2one(
        "res.partner", help="Matched against the delivery address of the sales order."
    )
    state_id = fields.Many2one(
        "res.country.state",
        domain="[('country_id', '=?', country_id)]",
        compute="_compute_state_id",
        inverse="_inverse_state_id",
        store=True,
        readonly=False,
        help="Matched against the state of the delivery address of the sales order.",
    )

    country_id = fields.Many2one(
        "res.country",
        compute="_compute_country_id",
        inverse="_inverse_country_id",
        store=True,
        readonly=False,
        help="Matched against the country of the delivery address of the sales order.",
    )
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )
    model_id = fields.Many2one("ir.model", required=True, ondelete="cascade")
    model_name = fields.Char(related="model_id.model", store=True)
    lead_time = fields.Float(string="Lead Time (Days)", required=True)

    @api.depends("partner_id", "partner_id.state_id")
    def _compute_state_id(self):
        for rec in self:
            rec.state_id = rec.partner_id.state_id if rec.partner_id else False

    @api.depends(
        "state_id", "state_id.country_id", "partner_id", "partner_id.country_id"
    )
    def _compute_country_id(self):
        for rec in self:
            if rec.state_id:
                rec.country_id = rec.state_id.country_id
            elif rec.partner_id:
                rec.country_id = rec.partner_id.country_id
            else:
                rec.country_id = False

    def _inverse_state_id(self):
        for rec in self:
            if rec.state_id:
                if rec.country_id != rec.state_id.country_id:
                    rec.country_id = rec.state_id.country_id
                if rec.partner_id and rec.partner_id.state_id != rec.state_id:
                    rec.partner_id = False
            else:
                if rec.partner_id and rec.country_id != rec.partner_id.country_id:
                    rec.country_id = rec.partner_id.country_id
                if rec.partner_id and rec.partner_id.state_id:
                    rec.partner_id = False

    def _inverse_country_id(self):
        for rec in self:
            if rec.state_id and rec.state_id.country_id != rec.country_id:
                rec.state_id = False
            if rec.partner_id and rec.partner_id.country_id != rec.country_id:
                rec.partner_id = False

    def _get_score(self, **kwargs):
        """Return a matching score for this lead time profile.

        The method scores each relevant match (warehouse/country/state/partner)
        based on factors defined in the company. For example, if the partner matches,
        the score is increased by the lead_time_profile_partner_factor. If any mismatch
        is found, it immediately returns -1.

        :param kwargs: Dictionary containing 'warehouse' and 'partner'.
        :return: A float representing the total match score if no mismatch is found,
            or -1 if any mismatch is found.
        """
        self.ensure_one()
        score = 0
        partner = kwargs.get("partner")
        warehouse = kwargs.get("warehouse")
        company = self.company_id
        if self.partner_id:
            if partner == self.partner_id:
                score += company.lead_time_profile_partner_factor
            else:
                return -1
        if self.state_id:
            if partner.state_id == self.state_id:
                score += company.lead_time_profile_state_factor
            else:
                return -1
        if self.country_id:
            if partner.country_id == self.country_id:
                score += company.lead_time_profile_country_factor
            else:
                return -1
        if self.warehouse_id:
            if warehouse == self.warehouse_id:
                score += company.lead_time_profile_warehouse_factor
            else:
                return -1
        return score
