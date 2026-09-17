Warehouse teams sometimes need to temporarily protect specific stock from
standard reservations, for example for quality checks, customer claims,
investigation, or internal allocation decisions. In standard usage, free
stock can still be consumed by other transfers, which makes these temporary
holds hard to enforce and hard to audit.

This module addresses that business need by using native Odoo reservation
mechanisms instead of introducing a parallel lock system. A dedicated lock
transfer is created and reserves the free quantity of a selected quant.
Because the lock is represented as standard stock documents, operations teams
keep full traceability and can reuse native stock workflows for review.

The module is especially useful in multi-user environments where concurrent
reservations are frequent and temporary stock holds must remain explicit,
reversible, and auditable.
