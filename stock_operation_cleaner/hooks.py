# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import mock
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    _logger.info("Remove pack ops linked to cancelled stock move")

    env = api.Environment(cr, SUPERUSER_ID, {})
    cancelled_moves = env["stock.move"].search([("state", "=", "cancel")])
    # mock the state since it's not allowed to remove pack operation on picking
    # done or cancelled
    pack_op_cls = env["stock.pack.operation"].__class__
    with mock.patch.object(pack_op_cls, "state", return_value="waiting"):
        cancelled_moves._delete_pack_ops()
