import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def create_inter_warehouse_routes(env):
    _logger.info("Creating missing routes...")
    env["res.company"].create_missing_route()


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    create_inter_warehouse_routes(env)
