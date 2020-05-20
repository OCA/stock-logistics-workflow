# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


def _default_sequence(record):
    maxrule = record.search([], order="sequence desc", limit=1)
    if maxrule:
        return maxrule.sequence + 10
    else:
        return 0


class StockSourceRelocate(models.Model):
    """Rules for move source relocating

    Each rule can have many removal rules, they configure the conditions and
    advanced removal strategies to apply on a specific location (sub-location
    of the rule).

    The rules are selected for a move based on their source location and a
    configurable domain on the rule.
    """

    _name = "stock.source.relocate"
    _description = "Stock Move Source Relocate"
    _order = "sequence, id"

    sequence = fields.Integer(default=lambda s: _default_sequence(s))
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        comodel_name="res.company", default=lambda self: self.env.user.company_id.id
    )

    location_id = fields.Many2one(comodel_name="stock.location", required=True)
    relocate_location_id = fields.Many2one(comodel_name="stock.location", required=True)
    picking_type_id = fields.Many2one(comodel_name="stock.picking.type", required=True)

    rule_domain = fields.Char(
        string="Rule Domain",
        default=[],
        help="Domain based on Stock Moves, to define if the "
        "rule is applicable or not.",
    )
    rule_message = fields.Html(compute="_compute_rule_message")

    @api.constrains("relocate_location_id")
    def _constraint_relocate_location_id(self):
        """The relocate location has to be a child of the main location."""
        for rule in self:
            if not rule.relocate_location_id.is_sublocation_of(rule.location_id):
                msg = _("Relocate location has to be a sub-location of '{}'.").format(
                    rule.location_id.display_name
                )
                raise ValidationError(msg)

    def _rule_message_template(self):
        message = _(
            "When a move with operation type "
            "<strong>{rule.picking_type_id.display_name}</strong>"
            " is inside the location"
            " <strong>{rule.location_id.display_name}</strong> and a check of"
            " availability returns no reservation, the move is relocated"
            " to the location"
            " <strong>{rule.relocate_location_id.display_name}</strong>"
            " (source location changed).<br/>"
            "If a move is partially unavailable, the move is split in two"
            " parts:<ul>"
            "<li>the available part is adjusted to the reserved quantity,"
            " and its source location stays the same </li>"
            "<li>the unavailable part is split in a new move in the"
            " relocation location</li>"
            "</ul>"
        )
        # we need to eval the domain to see if it's not "[]"
        if safe_eval(self.rule_domain) or []:
            message += _(
                "<br/>"
                "This rule is applied only if the <strong>domain</strong>"
                " matches with the move."
            )
        return message

    @api.depends(
        "location_id", "relocate_location_id", "picking_type_id", "rule_domain"
    )
    def _compute_rule_message(self):
        """Generate dynamically describing the rule for humans"""
        for rule in self:
            if not (
                rule.picking_type_id and rule.location_id and rule.relocate_location_id
            ):
                rule.rule_message = ""
                continue
            rule.rule_message = rule._rule_message_template().format(rule=rule)

    def name_get(self):
        res = []
        for record in self:
            res.append(
                (
                    record.id,
                    "{} → {}".format(
                        self.location_id.display_name,
                        self.relocate_location_id.display_name,
                    ),
                )
            )
        return res

    def _rule_for_move(self, move):
        rules = self.search(
            [
                ("picking_type_id", "=", move.picking_type_id.id),
                ("location_id", "parent_of", move.location_id.id),
            ]
        )
        for rule in rules:
            if rule._is_rule_applicable(move):
                return rule
        return self.browse()

    def _eval_rule_domain(self, move, domain):
        move_domain = [("id", "=", move.id)]
        # Warning: if we build a domain with dotted path such
        # as group_id.is_urgent (hypothetic field), can become very
        # slow as odoo searches all "procurement.group.is_urgent" first
        # then uses "IN group_ids" on the stock move only.
        # In such situations, it can be better either to add a related
        # field on the stock.move, either extend _eval_rule_domain to
        # add your own logic (based on SQL, ...).
        return bool(
            self.env["stock.move"].search(
                expression.AND([move_domain, domain]), limit=1
            )
        )

    def _is_rule_applicable(self, move):
        domain = safe_eval(self.rule_domain) or []
        if domain:
            return self._eval_rule_domain(move, domain)
        return True
