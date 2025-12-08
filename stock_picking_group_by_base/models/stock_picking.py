# Copyright 2016-2020 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2019-2020 Camptocamp
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from psycopg2.errors import LockNotAvailable

from odoo import api, models
from odoo.tools import SQL

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def _get_index_for_grouping_fields(self):
        """
        This tuple is intended to be overriden in order to add fields
        used in groupings
        """
        return [
            "partner_id",
            "location_id",
            "location_dest_id",
            "picking_type_id",
        ]

    @api.model
    def _get_index_for_grouping_condition(self):
        return """
            WHERE printed is False
            AND state in (
                'draft', 'confirmed', 'waiting',
                'partially_available', 'assigned'
            )
        """

    @api.model
    def _create_index_for_grouping(self):
        # create index for the domain expressed into the
        # stock_move._assign_picking_group_domain method
        index_name = "stock_picking_groupby_key_index"

        try:
            self.env.cr.execute(
                SQL(
                    "DROP INDEX IF EXISTS %(index_name)s",
                    index_name=SQL.identifier(index_name),
                )
            )

            self.env.cr.execute(
                SQL(
                    """
                    CREATE INDEX %(index_name)s
                    ON %(table_name)s (%(fields)s)
                    %(where)s
                """,
                    index_name=SQL.identifier(index_name),
                    table_name=SQL.identifier(self._table),
                    fields=SQL(", ").join(
                        [
                            SQL.identifier(field)
                            for field in self._get_index_for_grouping_fields()
                        ]
                    ),
                    where=SQL(self._get_index_for_grouping_condition()),
                )
            )
        except LockNotAvailable as e:
            # Do nothing and let module load
            _logger.warning(
                self.env._(
                    "Impossible to create index in stock_picking_group_by_base module"
                    " due to DB Lock problem (%s)",
                    e,
                )
            )
        except Exception:
            raise

    def init(self):
        """
        This has to be called in every overriding module
        """
        self._create_index_for_grouping()
