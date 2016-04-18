# -*- coding: utf-8 -*-
# © 2012-2014 Guewen Baconnier, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import date
from openerp import _, api, fields, models


class PickingDispatchStart(models.TransientModel):
    _name = 'picking.dispatch.start'
    _description = 'Picking Dispatch Start'

    def _get_message(self):
        selected_count = len(self.env.context['active_ids'])

        assigned_count = self.env['picking.dispatch'].search_count(
            self._get_assigned_domain()
        )

        message = "<ul><li>%s</li>" % _(
            "%s dispatch(es) will be started"
        ) % assigned_count

        if selected_count != assigned_count:
            message += "<li>%s</li>" % _(
                "%s dispatch(es) ignored because current state "
                "is not 'Assigned' or date is not reached"
            ) % (selected_count - assigned_count)
        message += "</ul>"

        return message

    message = fields.Html(readonly=True, default=_get_message)

    @api.multi
    def start(self):
        assigned_dispatches = self.env['picking.dispatch'].search(
            self._get_assigned_domain()
        )
        assigned_dispatches.action_progress()

    def _get_assigned_domain(self):
        """ Return the domain to use for searching startable picking distpatch.

        :rtype: list
        """
        return [
            ('id', 'in', self.env.context['active_ids']),
            ('state', '=', 'assigned'),
            ('date', '<=', date.today())
        ]
