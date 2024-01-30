from odoo import _, fields
from odoo.exceptions import UserError


def check_date(date):
    now = fields.Datetime.now()
    if date and date > now:
        raise UserError(_("You can not process an actual movement date in the future."))
