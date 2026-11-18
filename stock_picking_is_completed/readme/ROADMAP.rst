The 'is_completed' status field is not updated until picking is not saved.

This is due to how the framework is managing computed fields that are not
stored. In fact, the field on which we fill in the quantity is
'move_ids_without_package' and not 'move_line_ids' nor 'move_ids', so
the compute is not triggered.

It seems that adding it in the depends() solved the interface refresh when
we change the line quantity. But this introduces a warning in the log
as we depends on a non stored field ('move_ids_without_package').
