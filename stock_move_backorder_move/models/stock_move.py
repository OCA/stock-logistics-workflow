# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class StockMove(models.Model):

    _inherit = "stock.move"
    _parent_store = True

    parent_id = fields.Many2one(
        comodel_name="stock.move",
        string="Move Split From",
        index=True,
        ondelete="cascade",
        help="This move comes from another one. This happens when a backorder"
        " occured on that one.",
    )
    child_ids = fields.One2many(
        comodel_name="stock.move",
        inverse_name="parent_id",
        string="Move splitted in",
        help="In case of backorders, this move had been splitted with the"
        " remaining quantities to one or several other moves",
    )
    descendant_ids = fields.One2many(
        comodel_name="stock.move", compute="_compute_descendant_ids",
    )
    ancestor_ids = fields.One2many(
        comodel_name="stock.move", compute="_compute_ancestor_ids",
    )
    parent_path = fields.Char(index=True)

    def _prepare_move_split_vals(self, qty):
        res = super()._prepare_move_split_vals(qty)
        res["parent_id"] = self.id
        return res

    def _compute_descendant_ids(self):
        move_with_childs = self.filtered("child_ids")
        move_without_childs = self - move_with_childs
        void = self.browse()
        for move in move_without_childs:
            move.descendant_ids = void
        for move in move_with_childs:
            move.descendant_ids = self.search([("id", "child_of", move.id)])

    def show_descendant_moves(self):
        self.ensure_one()
        return {
            "name": _("Descendant Moves"),
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "stock.move",
            "domain": [("id", "child_of", self.id), ("id", "!=", self.id)],
        }

    def show_ancestor_moves(self):
        self.ensure_one()
        return {
            "name": _("Ancestor Moves"),
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "stock.move",
            "domain": [("id", "in", self.ancestor_ids.ids)],
        }

    def _find_move_ancestors(self):
        """Find the first level ancestors of given move
        The method is copied from stock.py to be callable with the new api
        """
        self.ensure_one()
        ancestors = self.browse()
        move2 = self
        while move2:
            ancestors |= move2.parent_id
            # loop on the split_from to find the ancestor of split moves only
            # if the move has not direct ancestor (priority goes to them)
            move2 = move2.parent_id
        return ancestors

    @api.depends("parent_id")
    def _compute_ancestor_ids(self):
        move_with_parent = self.filtered("parent_id")
        move_without_parent = self - move_with_parent
        void = self.browse()
        for move in move_without_parent:
            move.ancestor_ids = void
        for move in move_with_parent:
            move.ancestor_ids = move._find_move_ancestors()
