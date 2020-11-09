# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, SUPERUSER_ID
from . import models


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    picking_types = env["stock.picking.type"].search(
        [("owner_restriction", "!=", False)]
    )
    picking_types.write({"owner_restriction": False})


def set_default_owner_restriction(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    picking_types = env["stock.picking.type"].search(
        [("owner_restriction", "=", False)]
    )
    picking_types.write({"owner_restriction": "standard_behavior"})
