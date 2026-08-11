# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from . import models


def uninstall_hook(env):
    picking_types = (
        env["stock.picking.type"]
        .with_context(active_test=False)
        .search([("owner_restriction", "!=", False)])
    )
    picking_types.write({"owner_restriction": False})


def set_default_owner_restriction(env):
    picking_types = (
        env["stock.picking.type"]
        .with_context(active_test=False)
        .search([("owner_restriction", "=", False)])
    )
    picking_types.write({"owner_restriction": "standard_behavior"})
