# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID
from odoo.api import Environment


def no_default_immediate_tranfer_create(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    env["ir.config_parameter"].set_param("stock.no_default_immediate_tranfer", "True")
