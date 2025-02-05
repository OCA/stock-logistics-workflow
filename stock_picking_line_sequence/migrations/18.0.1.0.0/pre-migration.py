from odoo.tools.sql import column_exists, rename_column


def migrate(cr, version):
    """Rename sequence2 to visible_sequence like the other *_line_sequence modules"""
    table = "stock_move"
    old_column = "sequence2"
    new_column = "visible_sequence"
    if column_exists(cr, table, old_column) and not column_exists(
        cr, table, new_column
    ):
        rename_column(cr, table, old_column, new_column)
