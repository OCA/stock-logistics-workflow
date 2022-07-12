* This module only impacts the scheduler triggered by the cron, but you might still get automatic reservations in some other cases.
* On most databases, picking automatic reservation will be enabled by default. This affects StockMove._trigger_assign, that's usually called when completing manufacturing orders or receptions.
* There's also the procurement_jit module that's installed by default, and it will also attempt to reserve automatically upon SO confirmation.
