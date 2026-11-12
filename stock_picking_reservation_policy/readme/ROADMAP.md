A third reservation policy, *All or nothing per transfer* (`all`), is
planned.

Where *All or nothing per line* applies the all-or-nothing rule
independently to each line (stock move), *All or nothing per transfer*
would apply it to the whole transfer at once: the transfer is reserved
only if **every** one of its stock-sourced lines can be fully reserved;
if any line falls short, none of the transfer's lines are reserved.

This is not implemented yet.
