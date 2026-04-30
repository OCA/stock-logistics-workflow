This module is useful whenever a transfer has upstream pickings that must be
completed before it can proceed. The two most common scenarios are:

- **Multi-step outbound / inbound** configured on the warehouse (e.g. a 3-step
  delivery: `PICK → PACK → OUT`). The final OUT picking benefits from showing
  the state of the PICK and PACK operations without navigating to them.
- **Linked moves via route / rules logic**: push or pull rules can chain
  pickings across locations. Any downstream picking whose moves are fed by
  upstream moves will have an origin state computed.

When several origin pickings exist at the same chain level, the least
favorable state is reported.
