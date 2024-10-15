# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.exceptions import ValidationError


class DimensionRequiredError(ValidationError):
    def __init__(self, env):
        self.env = env
        super().__init__(_("At least one dimension must be set"))


class DimensionMustBePositiveError(ValidationError):
    def __init__(self, env, field):
        self.env = env
        field_label = field._description_string(self.env)
        super().__init__(
            _("Value of '%(field_label)s' must be positive", field_label=field_label)
        )
