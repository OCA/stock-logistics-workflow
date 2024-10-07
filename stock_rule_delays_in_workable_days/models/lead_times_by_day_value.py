# Copyright 2024 Foodles (https://www.foodles.co/).
# @author Alexandre Galdeano <alexandre.galdeano@foodles.co>
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression


class LeadTime(models.Model):
    _name = "lead_times_by_day.value"
    _description = "Lead times by day value"

    _order = "value"

    value = fields.Integer(string="Lead day", required=True)

    @api.constrains("value")
    def _check_value(self):
        for record in self:
            if record.value < 0:
                raise ValidationError(_("The value can't be negative"))

    def name_get(self):
        result = []
        for record in self:
            name = _("{} day(s)").format(record.value)
            result.append((record.id, name))
        return result

    @api.model
    def _name_search(
        self, name="", args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        args = args or []
        domain = expression.AND([[("value", operator, name)], args])
        return self._search(domain, limit=limit, access_rights_uid=name_get_uid)

    def get_or_create_by_value(self, value):
        record = self.search([("value", "=", value)], limit=1)
        if not record:
            record = self.create({"value": value})
        return record
