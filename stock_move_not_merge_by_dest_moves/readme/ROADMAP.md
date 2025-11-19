- Receipts (second step quantities not correct)

  Symptom: After testing receipts, the quantities shown/propagated in the second step are not correct (they do not match what was processed in the first step, or the distribution per move is inconsistent).

  Source: Video “Moduon - Review Gelo [16.0][ADD] stock_move_not_merge_by_dest_moves #2014”.
  https://www.loom.com/share/416b1efb65d04c5d80acd9fac2bf4e0f?sid=8084079a-d28b-4b04-9839-cf3544cddc42

  Expected: The second-step document should reflect the quantities done in the first step, line by line / per destination move, without over- or under-allocation.
  Actual: The second-step quantities differ from the first step and/or are misallocated.
  Status: Under investigation.

- Sales (SO line changes not updated on picking)

  Symptom: After confirming a Sales Order, changes made on the SO line are not propagated to the generated picking.

  Source: Video “Moduon - Review Gelo [16.0][ADD] stock_move_not_merge_by_dest_moves #2014 sales”.
  https://www.loom.com/share/8dfe51327d6d435f8dbdcef4af9ce77b?sid=424232ef-c392-4903-8d42-0254da24c812

  Expected: Updates on the SO line (e.g., quantity/discount that affect downstream moves) should be reflected on the generated picking.
  Actual: The picking does not refresh after SO line changes.
  Status: Under investigation.
