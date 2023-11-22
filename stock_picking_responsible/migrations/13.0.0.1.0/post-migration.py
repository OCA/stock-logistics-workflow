# Copyright 2022 Coop IT Easy SC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info(
        "stock_picking_responsible: migrate responsible_id to user_id."
        " Legacy column: legacy_13_0_responsible_id"
    )
    # env = api.Environment(cr, SUPERUSER_ID, {})

    # log missing users
    cr.execute(
        """
        SELECT sp.id AS picking_id,
               sp.name as picking_name,
               rp.id AS partner_id,
               rp.name as partner_name
        FROM stock_picking sp
                 JOIN res_partner rp ON rp.id = sp.responsible_id
                 LEFT JOIN res_users ru ON rp.id = ru.partner_id
        WHERE ru.id IS NULL
    """
    )
    partner_wo_user = cr.fetchall()
    for picking_id, picking_name, partner_id, partner_name in partner_wo_user:
        _logger.warning(
            f"Picking (%{picking_id}) {picking_name}:"
            f" cannot match user to ({partner_id}) {partner_name}"
        )

    # map responsible_id to user_id
    cr.execute(
        """
        WITH partner_user AS (
                      SELECT sp.id AS picking_id,
                             rp.id AS partner_id,
                             ru.id AS user_id
                      FROM stock_picking sp
                               JOIN res_partner rp ON rp.id = sp.responsible_id
                               LEFT join res_users ru ON rp.id = ru.partner_id)
        UPDATE stock_picking
        SET user_id = partner_user.user_id
        FROM partner_user
        WHERE stock_picking.id = partner_user.picking_id;
    """
    )
