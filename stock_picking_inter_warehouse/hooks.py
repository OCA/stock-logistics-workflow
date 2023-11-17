from odoo import SUPERUSER_ID, api


def create_inter_warehouse_routes(env):
    env["res.company"].create_missing_route()


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    create_inter_warehouse_routes(env)
