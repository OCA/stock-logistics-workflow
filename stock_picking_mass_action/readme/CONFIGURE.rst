* The scheduled action by default search picking with state is confirmed and picking_type_code is outgoing. But you can change it by adding the following param domain in method check_assign_all():

    - domain: correct domain to search pickings you want to check assign all, state is confirmed apply by default in all cases.

    .. code-block:: python
        
        # Example 1: search without params
        model.check_assign_all()
        # Example 2: search picking with picking_type_code is outgoing and incoming and state is confirmed
        model.check_assign_all(domain=[("picking_type_code", "in", ["outgoing", "incoming"])])
