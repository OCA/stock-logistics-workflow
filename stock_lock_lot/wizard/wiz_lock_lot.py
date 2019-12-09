# © 2015 Serv. Tec. Avanzados - Pedro M. Baeza (http://www.serviciosbaeza.com)
# © 2015 AvanzOsc (http://www.avanzosc.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class WizLockLot(models.TransientModel):
    _name = "wiz.lock.lot"

    @api.multi
    def action_lock_lots(self):
        lot_obj = self.env["stock.production.lot"]
        active_ids = self._context["active_ids"]
        lot_obj.browse(active_ids).button_lock()

    @api.multi
    def action_unlock_lots(self):
        lot_obj = self.env["stock.production.lot"]
        active_ids = self._context["active_ids"]
        lot_obj.browse(active_ids).button_unlock()
