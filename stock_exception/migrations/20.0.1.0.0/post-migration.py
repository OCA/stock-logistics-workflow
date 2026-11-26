# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
import logging
import re

_logger = logging.getLogger(__name__)

# stock.move.product_uom is uom_id in 20.0
RENAMES = {
    "stock.move": [(re.compile(r"\bproduct_uom\b"), "uom_id")],
    "stock.picking": [(re.compile(r"\bmove_ids\.product_uom\b"), "move_ids.uom_id")],
}
REMOVED = re.compile(r"\b(scrap_id|location_final_id|show_operations)\b")


def migrate(cr, version):
    cr.execute(
        """
        SELECT id, COALESCE(name->>'en_US', name::text), model, domain, code
          FROM exception_rule
         WHERE model IN ('stock.move', 'stock.picking')
        """
    )
    for rule_id, name, model, domain, code in cr.fetchall():
        new_domain, new_code = domain, code
        for pattern, repl in RENAMES[model]:
            new_domain = new_domain and pattern.sub(repl, new_domain)
            new_code = new_code and pattern.sub(repl, new_code)
        if (new_domain, new_code) != (domain, code):
            cr.execute(
                "UPDATE exception_rule SET domain = %s, code = %s WHERE id = %s",
                (new_domain, new_code, rule_id),
            )
            _logger.info(
                "Exception rule %s (%s): product_uom renamed to uom_id", rule_id, name
            )
        if REMOVED.search(new_domain or "") or REMOVED.search(new_code or ""):
            _logger.warning(
                "Exception rule %s (%s) uses a field removed in 20.0, review it",
                rule_id,
                name,
            )
