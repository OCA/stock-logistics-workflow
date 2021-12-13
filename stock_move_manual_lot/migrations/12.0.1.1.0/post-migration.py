# Copyright 2021 Opener B.V. <stefan@opener.amsterdam>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    """
    Sync manual lots with transferred lots

    Sync manual lots to cover the following cases
    * an untracked product transferred without setting a manual lot
    * an update of a picking type to use manual lot selection
    """
    cr.execute(
        """
        update stock_move_line
        set manual_lot_id=lot_id
        where state = 'done'
        and manual_lot_id is distinct from lot_id
        """
    )
